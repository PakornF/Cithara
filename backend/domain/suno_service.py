import time
import requests
import threading
from django.conf import settings
from .models import MusicGenerationRequest, Song, GenerationStatus

def _build_prompt(req: MusicGenerationRequest) -> str:
    parts = []
    if req.custom_story:
        parts.append(req.custom_story)
    
    style_parts = []
    if req.genre: style_parts.append(req.genre)
    if req.mood: style_parts.append(req.mood)
    if req.voice_type: style_parts.append(req.voice_type)
    
    if style_parts:
        parts.append(f"Style: {', '.join(style_parts)}")
        
    if req.occasion:
        parts.append(f"Occasion/Theme: {req.occasion}")
        
    return " | ".join(parts)

def generate_suno_song_task(req_id: int):
    try:
        req = MusicGenerationRequest.objects.get(pk=req_id)
    except MusicGenerationRequest.DoesNotExist:
        return

    req.status = GenerationStatus.INPROGRESS
    req.error_message = None
    req.save(update_fields=['status', 'error_message'])

    api_key = getattr(settings, 'SUNO_AI_API_KEY', None)
    base_url = getattr(settings, 'SUNO_API_BASE_URL', 'https://api.sunoapi.org').rstrip('/')

    if not api_key:
        req.status = GenerationStatus.FAILED
        req.error_message = "SUNO_AI_API_KEY not configured in settings."
        req.save(update_fields=['status', 'error_message'])
        return

    prompt = _build_prompt(req)
    req.prompt_generated = prompt
    req.save(update_fields=['prompt_generated'])

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        url = f"{base_url}/api/v1/generate"
        payload = {
            "customMode": False,
            "instrumental": False,
            "model": "V4_5",
            "callBackUrl": "https://webhook.site/dummy",
            "prompt": f"{req.title}. {prompt}"
        }
        
        res = requests.post(url, json=payload, headers=headers, timeout=120)

        # Fallback if 404 (just in case they are using a non-v1 suno-api container)
        if res.status_code == 404:
            url = f"{base_url}/api/generate"
            res = requests.post(url, json={"prompt": prompt, "make_instrumental": False}, headers=headers, timeout=120)

        res.raise_for_status()
        data = res.json() or {}
        
        task_id = (data.get('data') or {}).get('taskId')
        audio_url = None
        
        if task_id:
            # V1 Polling
            for _ in range(60):
                time.sleep(5)
                poll_res = requests.get(f"{base_url}/api/v1/generate/record-info?taskId={task_id}", headers=headers, timeout=15)
                if poll_res.ok:
                    poll_data = poll_res.json() or {}
                    task_data = poll_data.get('data') or {}
                    poll_status = task_data.get('status', '')
                    if poll_status == 'SUCCESS':
                        response_data = task_data.get('response') or {}
                        suno_data = response_data.get('sunoData') or []
                        if suno_data and len(suno_data) > 0:
                            clip = suno_data[0] or {}
                            audio_url = clip.get('audioUrl') or clip.get('streamAudioUrl')
                            if audio_url:
                                break
                    elif poll_status in ('CREATE_TASK_FAILED', 'GENERATE_AUDIO_FAILED'):
                        raise Exception(f"Suno API returned error status: {poll_status}")
        else:
            # Fallback legacy parsing
            clips = data.get('data') or data.get('clips') or data
            if isinstance(clips, list) and len(clips) > 0:
                clip = clips[0] or {}
            elif isinstance(clips, dict) and 'id' in clips:
                clip = clips
            else:
                raise Exception("Invalid API response format")

            audio_url = clip.get('audio_url')
            clip_id = clip.get('id')

            if not audio_url and clip_id:
                for _ in range(60): 
                    time.sleep(5)
                    poll_url = f"{base_url}/api/get?ids={clip_id}"
                    poll_res = requests.get(poll_url, headers=headers, timeout=15)
                    if poll_res.ok:
                        poll_data = poll_res.json() or {}
                        arr = poll_data.get('data') or poll_data.get('clips') or poll_data
                        if isinstance(arr, list) and len(arr) > 0:
                            arr_0 = arr[0] or {}
                            poll_status = arr_0.get('status', '')
                            if poll_status == 'complete' or poll_status == 'streaming':
                                audio_url = arr_0.get('audio_url')
                                if audio_url:
                                    break
                            elif poll_status == 'error':
                                raise Exception("Suno API returned error status during generation.")

        if not audio_url:
            raise Exception("Timed out waiting for audio URL from Suno AI.")

        song = Song.objects.create(
            owner=req.user,
            title=req.title,
            genre=req.genre,
            mood=req.mood,
            occasion=req.occasion,
            voice_type=req.voice_type,
            status=GenerationStatus.COMPLETED,
            audio_file_path=audio_url,
            prompt_used=prompt
        )

        req.song = song
        req.status = GenerationStatus.COMPLETED
        req.save(update_fields=['song', 'status'])

    except Exception as e:
        req.status = GenerationStatus.FAILED
        req.error_message = str(e)
        req.save(update_fields=['status', 'error_message'])

def launch_generation_thread(req_id: int):
    t = threading.Thread(target=generate_suno_song_task, args=(req_id,))
    t.daemon = True
    t.start()
