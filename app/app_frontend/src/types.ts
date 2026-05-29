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

export type EditProfileForm = {
  username: string
  email: string
  oldPassword: string
  password: string
}

export type UserProfile = {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
}

export type CollaboratorRole = 'READER' | 'EDITOR' | 'ADMIN'
export type ResourceAccessRole = CollaboratorRole | 'OWNER' | null

export type CollaboratorSummary = {
  id: number
  user_id: number
  username: string
  email: string
  role: CollaboratorRole
}

export type Collaboration = {
  id: number
  user: number
  user_detail?: UserProfile
  owner?: UserProfile
  resource_type: 'TASK' | 'PROJECT'
  task: number | null
  project: number | null
  resource_name?: string
  role: CollaboratorRole
  assigned_at: string
}

export type ShareForm = {
  userIdentifier: string
  role: CollaboratorRole
}

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH'
export type TaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export type Task = {
  id: number
  owner?: UserProfile
  collaborators?: CollaboratorSummary[]
  project: number | null
  title: string
  description: string
  priority: TaskPriority
  status: TaskStatus
  due_date: string | null
  created_at: string
  updated_at: string
  is_owner?: boolean
  collaboration_role?: ResourceAccessRole
  can_edit?: boolean
  can_invite_collaborators?: boolean
}

export type TaskForm = {
  title: string
  description: string
  priority: TaskPriority
  status: TaskStatus
  due_date: string
  project: string
}

export type Project = {
  id: number
  owner?: UserProfile
  collaborators?: CollaboratorSummary[]
  name: string
  description: string
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
  tasks_count?: number
  completed_tasks_count?: number
  progress_percentage?: number
  is_owner?: boolean
  collaboration_role?: ResourceAccessRole
  can_edit?: boolean
  can_invite_collaborators?: boolean
}

export type ProjectForm = {
  name: string
  description: string
  start_date: string
  end_date: string
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
  statusClass: string
}


export type CalendarItem = {
  type: 'task' | 'project_start' | 'project_end'
  id: number
  title: string
  date: string
  status?: TaskStatus
  priority?: TaskPriority
}

export type CalendarData = {
  view: 'day' | 'week' | 'month'
  start_date: string
  end_date: string
  items: CalendarItem[]
}
