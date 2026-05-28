export type AuthMode = 'register' | 'login'

export type RegisterForm = {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export type LoginForm = {
  username: string
  password: string
}

export type UserProfile = {
  id: number
  username: string
  email: string
  first_name?: string
}

export type Task = {
  id: number
  title: string
  description: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  due_date: string | null
  updated_at: string
}

export type Project = {
  id: number
  name: string
  description: string
  start_date: string | null
  end_date: string | null
}

export type DashboardData = {
  metric?: {
    tasks_created: number
    tasks_completed: number
    effective_minutes: number
  }
  tasks_by_status?: Record<string, number>
  project_progress?: Array<{ project_id: number; project: string; progress_percentage: number }>
}

export type DashboardTaskItem = {
  id: number
  title: string
  dateLabel: string
}

export type ActivityItem = {
  id: number
  title: string
  statusLabel: string
  isPending: boolean
}
