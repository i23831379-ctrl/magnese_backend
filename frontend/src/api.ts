import type { 
  ManganesePrediction, 
  ManganesePredictionRequest, 
  ModelStatus, 
  Target, 
  ProspectivityFeature, 
  TrainingDataValidation 
} from './types'

// Safely get and format the API URL from environment variables, removing any trailing slashes
const getApiUrl = (): string => {
  const envUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
  const rawUrl = envUrl || 'https://magnese-backend.onrender.com/api';
  return rawUrl.replace(/\/+$/, ''); // Strip trailing slashes to avoid double-slash issues
};

export const API_URL = getApiUrl();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const endpoint = `${API_URL}${cleanPath}`;

  try {
    const res = await fetch(endpoint, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    });

    if (!res.ok) {
      const errorBody = await res.text().catch(() => '');
      throw new Error(`API request failed [${res.status}]: ${errorBody || res.statusText}`);
    }

    return res.json();
  } catch (error) {
    console.error(`[API Error] Failed to fetch ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  targets: () => request<Target[]>('/manganese/targets'),
  target: (id: number) => request<Target>(`/manganese/targets/${id}`),
  prospectivity: () => request<{ type: string; features: ProspectivityFeature[] }>('/manganese/prospectivity'),
  predictManganese: (payload: ManganesePredictionRequest) => 
    request<ManganesePrediction>('/manganese/predict', { 
      method: 'POST', 
      body: JSON.stringify(payload) 
    }),
  manganeseModelStatus: () => request<ModelStatus>('/manganese/model/status'),
  uploadManganeseData: (csvText: string) => 
    request<TrainingDataValidation>('/manganese/upload-data', { 
      method: 'POST', 
      body: JSON.stringify({ csv_text: csvText }) 
    }),
  health: () => request<{ status: string }>('/health'),
};
