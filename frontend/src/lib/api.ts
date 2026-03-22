// Call Django backend directly (CORS enabled). Set NEXT_PUBLIC_API_URL to override.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  const contentType = res.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");

  if (!res.ok) {
    const msg = isJson
      ? ((await res.json().catch(() => ({}))) as { error?: string })?.error
      : null;
    throw new Error(msg || `HTTP ${res.status}`);
  }
  if (res.status === 204) return {} as T;
  if (!isJson) {
    const text = await res.text();
    throw new Error(`Expected JSON but got: ${text.slice(0, 80)}...`);
  }
  return res.json();
}

export interface AuthUser {
  id: number;
  email: string;
  name: string;
}

export const api = {
  auth: {
    requestVerification: (data: { email: string; name: string; password: string }) =>
      fetchApi<{ sent: boolean; email: string }>('/auth/request-verification/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    verifyAndRegister: (data: { email: string; name: string; password: string; code: string }) =>
      fetchApi<AuthUser>('/auth/verify-and-register/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    login: (data: { email: string; password: string }) =>
      fetchApi<AuthUser>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    google: (credential: string) =>
      fetchApi<AuthUser>('/auth/google/', {
        method: 'POST',
        body: JSON.stringify({ credential }),
      }),
  },
  users: {
    list: () => fetchApi<import('./types').User[]>('/users/'),
    get: (id: number) => fetchApi<import('./types').User>(`/users/${id}/`),
    create: (data: { email: string; name: string; google_id?: string; password_hash?: string }) =>
      fetchApi<{ id: number; email: string; name: string }>('/users/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  songs: {
    list: (userId?: number) =>
      fetchApi<import('./types').Song[]>(userId ? `/songs/?user_id=${userId}` : '/songs/'),
    get: (id: number) => fetchApi<import('./types').SongDetail>(`/songs/${id}/`),
    create: (data: {
      owner_id: number;
      title: string;
      genre: string;
      mood: string;
      occasion: string;
      voice_type: string;
      custom_story?: string;
      status?: string;
      audio_file_path?: string;
    }) =>
      fetchApi<{ id: number; title: string; status: string }>('/songs/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<import('./types').SongDetail>) =>
      fetchApi<import('./types').SongDetail>(`/songs/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi<{ deleted: boolean }>(`/songs/${id}/`, { method: 'DELETE' }),
    createShareLink: (id: number) =>
      fetchApi<{ token: string; share_url: string; is_active: boolean }>(
        `/songs/${id}/share/`,
        { method: 'POST' }
      ),
  },
  requests: {
    list: (userId?: number) =>
      fetchApi<import('./types').MusicGenerationRequest[]>(
        userId ? `/requests/?user_id=${userId}` : '/requests/'
      ),
    get: (id: number) =>
      fetchApi<import('./types').MusicGenerationRequest & { timed_out?: boolean }>(
        `/requests/${id}/`
      ),
    create: (data: {
      user_id: number;
      title: string;
      genre: string;
      mood: string;
      occasion: string;
      voice_type: string;
      custom_story?: string;
      is_retry?: boolean;
    }) =>
      fetchApi<{ id: number; title: string; status: string; is_retry: boolean }>(
        '/requests/',
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      ),
  },
  share: {
    get: (token: string) =>
      fetchApi<import('./types').SharedSong>(`/share/${token}/`),
  },
  feedback: {
    create: (data: {
      user_id: number;
      song_id?: number;
      feedback_text: string;
    }) =>
      fetchApi<{ id: number; submitted_at: string }>('/feedback/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};
