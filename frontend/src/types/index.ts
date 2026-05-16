// frontend/src/types/index.ts
export interface User {
  id: string
  email: string
  username: string
  full_name: string | null
  role: 'admin' | 'user' | 'guest'
  avatar_url: string | null
  created_at: string
}

export interface Project {
  id: string
  name: string
  description: string | null
  status: 'active' | 'archived' | 'training'
  owner_id: string
  active_model_id: string | null
  created_at: string
  updated_at: string
  dataset_stats?: {
    total_images: number
    good_samples: number
    defect_samples: number
    defect_classes: string[]
  }
}

export interface Defect {
  class_name: string
  confidence: number
  bbox?: [number, number, number, number]
  mask?: string
  area?: number
  centroid?: [number, number]
}

export interface InspectionResult {
  id: string
  project_id: string
  defects: Defect[]
  processing_time_ms: number
  image_url: string
  result_url: string
  created_at: string
}

export interface TrainingTask {
  task_id: string
  project_id: string
  status: 'queued' | 'preparing' | 'training' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_epoch?: number
  total_epochs?: number
  current_loss?: number
  metrics?: Record<string, number>
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface TrainingConfig {
  model_type: 'yolo' | 'anomalib' | 'sam' | 'auto'
  epochs: number
  batch_size: number
  learning_rate: number
  image_size: number
}