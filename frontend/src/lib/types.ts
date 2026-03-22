export type Genre = 'Pop' | 'Rock' | 'Jazz' | 'Classical' | 'Hiphop';
export type Mood = 'Happy' | 'Sad' | 'Romantic' | 'Energetic' | 'Calm';
export type Occasion = 'Birthday' | 'Wedding' | 'Graduation' | 'Anniversary' | 'Custom';
export type VoiceType = 'Male' | 'Female';
export type GenerationStatus =
  | 'Pending'
  | 'InProgress'
  | 'Completed'
  | 'Failed'
  | 'TimedOut'
  | 'Rejected';

export interface User {
  id: number;
  email: string;
  name: string;
  google_id?: string;
  created_at: string;
  last_login_at?: string;
}

export interface Song {
  id: number;
  title: string;
  genre: Genre;
  mood: Mood;
  occasion: Occasion;
  voice_type: VoiceType;
  status: GenerationStatus;
  creation_date: string;
  owner__name?: string;
  owner__email?: string;
  is_saved?: boolean;
  audio_file_path?: string;
}

export interface SongDetail extends Song {
  custom_story?: string;
  prompt_used?: string;
  audio_file_path?: string;
  duration?: number;
  owner: { id: number; name: string };
  share_link?: { token: string; is_active: boolean };
}

export interface MusicGenerationRequest {
  id: number;
  title: string;
  status: GenerationStatus;
  is_retry: boolean;
  submitted_at: string;
  genre: Genre;
  mood: Mood;
  voice_type: VoiceType;
  occasion: Occasion;
  error_message?: string;
  user__name?: string;
  song__id?: number;
}

export interface SharedSong {
  song_id: number;
  title: string;
  genre: Genre;
  mood: Mood;
  audio_file_path?: string;
}
