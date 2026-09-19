export type MineralType = 'manganese'

export type ProspectivityClass = 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'VERY_LOW'

export type Target = {
  id: number
  code: string
  name: string
  latitude: number
  longitude: number
  score: number
  confidence: number
  zone: 'HIGH' | 'MEDIUM' | 'LOW'
  geology: string
  status: 'Pending' | 'Validated' | 'Needs review'
  factors: string[]
  mineral: MineralType
  manganese_probability: number
  classification: ProspectivityClass
  priority: 'P1' | 'P2' | 'P3'
  feature_summary: string[]
  data_sources: string[]
  model_name: string
  model_version: string
  model_status: 'demo' | 'trained' | 'validated' | 'unavailable'
}

export type ManganesePredictionRequest = {
  latitude: number
  longitude: number
  features: Record<string, number>
}

export type ManganesePrediction = {
  mineral: MineralType
  latitude: number
  longitude: number
  manganese_probability: number
  confidence: number
  classification: ProspectivityClass
  priority: 'P1' | 'P2' | 'P3'
  feature_summary: string[]
  data_sources: string[]
  model_name: string
  model_version: string
  model_status: 'demo'
}

export type ModelStatus = {
  mineral: MineralType
  model_name: string
  version: string
  training_date: string | null
  feature_list: string[]
  status: 'demo' | 'trained' | 'validated' | 'unavailable'
  training_dataset: string
  record_count: number | null
  metrics: Record<string, number> | null
  message: string
}

export type TrainingDataValidation = {
  mineral: MineralType
  record_count: number
  feature_columns: string[]
  status: string
}

export type ProspectivityFeature = {
  type: 'Feature'
  properties: { mineral: 'manganese'; zone: string; score: number; manganese_probability: number; classification: ProspectivityClass; model_status: 'demo' }
  geometry: { type: 'Polygon'; coordinates: number[][][] }
}
