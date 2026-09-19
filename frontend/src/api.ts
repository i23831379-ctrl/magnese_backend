import type { ManganesePrediction, ManganesePredictionRequest, ModelStatus, Target, ProspectivityFeature, TrainingDataValidation } from './types'

export const API_URL = (import.meta.env.VITE_API_URL as string | undefined) || 'http://127.0.0.1:8000/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {'Content-Type': 'application/json', ...init?.headers},
  })
  if (!res.ok) throw new Error(`API request failed: ${res.status}`)
  return res.json()
}

export const api = {
  targets: () => request<Target[]>('/manganese/targets'),
  target: (id: number) => request<Target>(`/manganese/targets/${id}`),
  prospectivity: () => request<{type: string; features: ProspectivityFeature[]}>('/manganese/prospectivity'),
  predictManganese: (payload: ManganesePredictionRequest) => request<ManganesePrediction>('/manganese/predict', {method: 'POST', body: JSON.stringify(payload)}),
  manganeseModelStatus: () => request<ModelStatus>('/manganese/model/status'),
  uploadManganeseData: (csvText: string) => request<TrainingDataValidation>('/manganese/upload-data', {method: 'POST', body: JSON.stringify({csv_text: csvText})}),
  health: () => request<{status: string}>('/health'),
}
