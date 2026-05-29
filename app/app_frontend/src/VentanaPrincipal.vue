<script setup lang="ts">
import BotonVolver from './BotonVolver.vue'
import { computed, onMounted, ref } from 'vue'
import PantallaCalendario from './PantallaCalendario.vue'
import PantallaCrearProyecto from './PantallaCrearProyecto.vue'
import PantallaCrearTarea from './PantallaCrearTarea.vue'
import PantallaEditarPerfil from './PantallaEditarPerfil.vue'
import PantallaEditarProyecto from './PantallaEditarProyecto.vue'
import PantallaEditarTarea from './PantallaEditarTarea.vue'
import PantallaEliminarProyecto from './PantallaEliminarProyecto.vue'
import PantallaEliminarTarea from './PantallaEliminarTarea.vue'
import PantallaInicio from './PantallaInicio.vue'
import PantallaIniciarSesion from './PantallaIniciarSesion.vue'
import PantallaMisProyectos from './PantallaMisProyectos.vue'
import PantallaMisTareas from './PantallaMisTareas.vue'
import PantallaPerfil from './PantallaPerfil.vue'
import PantallaProyecto from './PantallaProyecto.vue'
import PantallaRegistro from './PantallaRegistro.vue'
import PantallaTarea from './PantallaTarea.vue'
import type {
  ActivityItem,
  AuthMode,
  CalendarData,
  CalendarItem,
  Collaboration,
  DashboardData,
  DashboardTaskItem,
  EditProfileForm,
  LoginForm,
  Project,
  ProjectForm,
  RegisterForm,
  ShareForm,
  Task,
  TaskForm,
  UserProfile,
} from './types'

const API_BASE = '/api'

type AppView =
  | 'auth'
  | 'dashboard'
  | 'profile'
  | 'edit-profile'
  | 'calendar'
  | 'tasks'
  | 'task-detail'
  | 'task-create'
  | 'task-edit'
  | 'task-delete'
  | 'projects'
  | 'project-detail'
  | 'project-create'
  | 'project-edit'
  | 'project-delete'

const currentView = ref<AppView>('auth')
const navigationHistory = ref<AppView[]>([])
const authMode = ref<AuthMode>('register')
const loading = ref(false)
const dashboardLoading = ref(false)
const calendarLoading = ref(false)
const authMessage = ref('')
const dashboardMessage = ref('')
const calendarMessage = ref('')
const editProfileMessage = ref('')
const profileSaving = ref(false)
const taskMessage = ref('')
const taskSaving = ref(false)
const projectMessage = ref('')
const projectSaving = ref(false)
const taskShareMessage = ref('')
const projectShareMessage = ref('')
const shareLoading = ref(false)
const calendarDate = ref(toIsoDate(new Date()))
const selectedTaskId = ref<number | null>(null)
const selectedProjectId = ref<number | null>(null)
const accessToken = ref(localStorage.getItem('access') || '')
const refreshToken = ref(localStorage.getItem('refresh') || '')

const registerForm = ref<RegisterForm>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const loginForm = ref<LoginForm>({
  username: '',
  password: '',
})

const editProfileForm = ref<EditProfileForm>({
  username: '',
  email: '',
  oldPassword: '',
  password: '',
})

const taskForm = ref<TaskForm>(emptyTaskForm())
const projectForm = ref<ProjectForm>(emptyProjectForm())
const taskShareForm = ref<ShareForm>(emptyShareForm())
const projectShareForm = ref<ShareForm>(emptyShareForm())

const profile = ref<UserProfile | null>(null)
const tasks = ref<Task[]>([])
const projects = ref<Project[]>([])
const dashboard = ref<DashboardData | null>(null)
const calendar = ref<CalendarData | null>(null)
const collaborations = ref<Collaboration[]>([])
const users = ref<UserProfile[]>([])

function emptyTaskForm(): TaskForm {
  return {
    title: '',
    description: '',
    priority: 'HIGH',
    status: 'PENDING',
    due_date: '',
    project: '',
  }
}

function emptyProjectForm(): ProjectForm {
  return {
    name: '',
    description: '',
    start_date: '',
    end_date: '',
  }
}

function emptyShareForm(): ShareForm {
  return {
    userIdentifier: '',
    role: 'READER',
  }
}

function resetRegisterForm() {
  registerForm.value = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  }
}

function resetLoginForm() {
  loginForm.value = {
    username: '',
    password: '',
  }
}

function clearAuthForms() {
  resetRegisterForm()
  resetLoginForm()
}

function resetEditProfileForm() {
  editProfileForm.value = {
    username: '',
    email: '',
    oldPassword: '',
    password: '',
  }
}

function resetTaskForm(task?: Task) {
  taskForm.value = task
    ? {
        title: task.title,
        description: task.description,
        priority: task.priority,
        status: task.status,
        due_date: task.due_date || '',
        project: task.project ? String(task.project) : '',
      }
    : emptyTaskForm()
}

function resetProjectForm(project?: Project) {
  projectForm.value = project
    ? {
        name: project.name,
        description: project.description,
        start_date: project.start_date || '',
        end_date: project.end_date || '',
      }
    : emptyProjectForm()
}

function resetTaskShareForm() {
  taskShareForm.value = emptyShareForm()
}

function resetProjectShareForm() {
  projectShareForm.value = emptyShareForm()
}

const displayName = computed(() => {
  const username = profile.value?.first_name || profile.value?.username || registerForm.value.username
  if (!username) return 'Jaime'
  return username.charAt(0).toUpperCase() + username.slice(1)
})

const initials = computed(() => displayName.value.slice(0, 1).toUpperCase())

const profileDisplayName = computed(() => {
  const firstName = profile.value?.first_name?.trim()
  const lastName = profile.value?.last_name?.trim()
  const fullName = [firstName, lastName].filter(Boolean).join(' ')
  return fullName || profile.value?.username || displayName.value
})

const profileUsername = computed(() => profile.value?.username || displayName.value)
const profileEmail = computed(() => profile.value?.email || '')
const selectedTask = computed(() => tasks.value.find((task) => task.id === selectedTaskId.value) || null)
const selectedProject = computed(() => projects.value.find((project) => project.id === selectedProjectId.value) || null)
const selectedProjectTasks = computed(() =>
  selectedProject.value ? tasks.value.filter((task) => task.project === selectedProject.value?.id) : [],
)
const selectedTaskCollaborations = computed(() =>
  selectedTask.value
    ? collaborations.value.filter((collaboration) => collaboration.task === selectedTask.value?.id)
    : [],
)
const selectedProjectCollaborations = computed(() =>
  selectedProject.value
    ? collaborations.value.filter((collaboration) => collaboration.project === selectedProject.value?.id)
    : [],
)
const canShareSelectedTask = computed(() => Boolean(selectedTask.value?.can_invite_collaborators))
const canShareSelectedProject = computed(() => Boolean(selectedProject.value?.can_invite_collaborators))

const pendingTasks = computed(() => tasks.value.filter((task) => task.status !== 'COMPLETED').length)
const completedTasks = computed(() => tasks.value.filter((task) => task.status === 'COMPLETED').length)
const activeProjects = computed(() => projects.value.length)
const effectiveMinutes = computed(() => dashboard.value?.metric?.effective_minutes || 0)

const upcomingTasks = computed<DashboardTaskItem[]>(() =>
  tasks.value
    .filter((task) => task.status !== 'COMPLETED')
    .sort((a, b) => (a.due_date || '9999').localeCompare(b.due_date || '9999'))
    .slice(0, 3)
    .map((task) => ({
      id: task.id,
      title: task.title,
      dateLabel: formatDate(task.due_date),
    })),
)

const recentActivity = computed<ActivityItem[]>(() =>
  [...tasks.value]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 3)
    .map((task) => ({
      id: task.id,
      title: task.title,
      statusLabel: statusLabel(task.status),
      statusClass: statusClass(task.status),
    })),
)

const canGoBack = computed(() => navigationHistory.value.some((view) => view !== currentView.value))

const showBackButton = computed(() =>
  canGoBack.value &&
  [
    'profile',
    'tasks',
    'task-detail',
    'task-create',
    'task-delete',
    'projects',
    'project-detail',
    'project-create',
    'project-delete',
  ].includes(currentView.value),
)

function setCurrentView(
  view: AppView,
  options: { remember?: boolean; clearHistory?: boolean } = {},
) {
  if (options.clearHistory) {
    navigationHistory.value = []
  } else if (options.remember !== false && currentView.value !== view) {
    navigationHistory.value = [...navigationHistory.value, currentView.value]
  }

  currentView.value = view
}

function saveTokens(access: string, refresh: string) {
  accessToken.value = access
  refreshToken.value = refresh
  localStorage.setItem('access', access)
  localStorage.setItem('refresh', refresh)
}

function clearTokens() {
  accessToken.value = ''
  refreshToken.value = ''
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
}

function extractError(payload: unknown): string {
  if (!payload || typeof payload !== 'object') return 'No se pudo completar la operacion.'
  const values = Object.values(payload as Record<string, unknown>).flat()
  const first = values[0]
  if (typeof first === 'string') return first
  if (Array.isArray(first) && typeof first[0] === 'string') return first[0]
  return 'Revisa los datos introducidos.'
}

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (!headers.has('Content-Type') && options.body) headers.set('Content-Type', 'application/json')
  if (accessToken.value) headers.set('Authorization', `Bearer ${accessToken.value}`)

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const text = await response.text()
  const payload = text ? JSON.parse(text) : null

  if (!response.ok) {
    throw new Error(extractError(payload))
  }
  return payload as T
}

async function login(username: string, password: string) {
  const tokenResponse = await apiRequest<{ access: string; refresh: string }>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  saveTokens(tokenResponse.access, tokenResponse.refresh)
}

async function submitRegister() {
  authMessage.value = ''
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    authMessage.value = 'Las contrasenas no coinciden.'
    return
  }

  loading.value = true
  try {
    await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        username: registerForm.value.username,
        email: registerForm.value.email,
        password: registerForm.value.password,
      }),
    })
    await login(registerForm.value.username, registerForm.value.password)
    await loadDashboard()
    clearAuthForms()
    authMessage.value = ''
    setCurrentView('dashboard', { clearHistory: true })
  } catch (error) {
    authMessage.value = error instanceof Error ? error.message : 'No se pudo crear la cuenta.'
  } finally {
    loading.value = false
  }
}

async function submitLogin() {
  authMessage.value = ''
  loading.value = true
  try {
    await login(loginForm.value.username, loginForm.value.password)
    await loadDashboard()
    clearAuthForms()
    authMessage.value = ''
    setCurrentView('dashboard', { clearHistory: true })
  } catch (error) {
    authMessage.value = error instanceof Error ? error.message : 'No se pudo iniciar sesion.'
  } finally {
    loading.value = false
  }
}

async function loadDashboard() {
  if (!accessToken.value) return
  dashboardLoading.value = true
  dashboardMessage.value = ''
  try {
    const [profileData, taskData, projectData, dashboardData, collaborationData, userData] = await Promise.all([
      apiRequest<UserProfile>('/auth/profile/'),
      apiRequest<Task[]>('/tasks/'),
      apiRequest<Project[]>('/projects/'),
      apiRequest<DashboardData>('/statistics/dashboard/'),
      apiRequest<Collaboration[]>('/collaborations/'),
      apiRequest<UserProfile[]>('/users/'),
    ])
    profile.value = profileData
    tasks.value = taskData
    projects.value = projectData
    dashboard.value = dashboardData
    collaborations.value = collaborationData
    users.value = userData
  } catch (error) {
    dashboardMessage.value = error instanceof Error ? error.message : 'No se pudo cargar el inicio.'
    clearTokens()
    setCurrentView('auth', { clearHistory: true })
  } finally {
    dashboardLoading.value = false
  }
}

function switchAuthMode(mode: AuthMode) {
  clearAuthForms()
  authMode.value = mode
  authMessage.value = ''
}

function handleNavigation(section: string) {
  if (section === 'inicio') openDashboard()
  if (section === 'tareas') openTasks()
  if (section === 'proyecto') openProjects()
  if (section === 'calendario') openCalendar()
}

function openProfile() {
  setCurrentView('profile')
}

function goBack() {
  let previous = navigationHistory.value.pop()
  while (previous && previous === currentView.value) {
    previous = navigationHistory.value.pop()
  }
  navigationHistory.value = [...navigationHistory.value]

  if (previous) {
    setCurrentView(previous, { remember: false })
  }
}

function openDashboard() {
  resetEditProfileForm()
  resetTaskForm()
  resetProjectForm()
  resetTaskShareForm()
  resetProjectShareForm()
  taskMessage.value = ''
  projectMessage.value = ''
  taskShareMessage.value = ''
  projectShareMessage.value = ''
  calendarMessage.value = ''
  setCurrentView('dashboard', { clearHistory: true })
}

function openEditProfile() {
  resetEditProfileForm()
  editProfileMessage.value = ''
  setCurrentView('edit-profile', { remember: false })
}

function cancelEditProfile() {
  resetEditProfileForm()
  editProfileMessage.value = ''
  setCurrentView('profile', { remember: false })
}

async function loadCalendar(date = calendarDate.value) {
  if (!accessToken.value) return
  calendarLoading.value = true
  calendarMessage.value = ''
  try {
    calendarDate.value = date
    calendar.value = await apiRequest<CalendarData>(`/calendar/?view=month&date=${date}`)
  } catch (error) {
    calendarMessage.value = error instanceof Error ? error.message : 'No se pudo cargar el calendario.'
  } finally {
    calendarLoading.value = false
  }
}

function openCalendar() {
  calendarMessage.value = ''
  setCurrentView('calendar')
  void loadDashboard()
  void loadCalendar()
}

function changeCalendarMonth(date: string) {
  void loadCalendar(date)
}

async function openCalendarItem(item: CalendarItem) {
  if (item.type === 'task') {
    let task = tasks.value.find((taskItem) => taskItem.id === item.id)
    if (!task) {
      await loadDashboard()
      task = tasks.value.find((taskItem) => taskItem.id === item.id)
    }
    if (task) openTaskDetail(task)
    return
  }

  let project = projects.value.find((projectItem) => projectItem.id === item.id)
  if (!project) {
    await loadDashboard()
    project = projects.value.find((projectItem) => projectItem.id === item.id)
  }
  if (project) openProjectDetail(project)
}

function openTasks(remember = true) {
  resetTaskForm()
  selectedTaskId.value = null
  taskMessage.value = ''
  setCurrentView('tasks', { remember })
  void loadDashboard()
}

function openTaskDetail(task: Task, remember = true) {
  selectedTaskId.value = task.id
  taskMessage.value = ''
  taskShareMessage.value = ''
  resetTaskShareForm()
  setCurrentView('task-detail', { remember })
}

function openCreateTask() {
  resetTaskForm()
  selectedTaskId.value = null
  taskMessage.value = ''
  setCurrentView('task-create')
}

function openEditTask(task: Task) {
  selectedTaskId.value = task.id
  resetTaskForm(task)
  taskMessage.value = ''
  setCurrentView('task-edit', { remember: false })
}

function openDeleteTask(task: Task) {
  selectedTaskId.value = task.id
  taskMessage.value = ''
  setCurrentView('task-delete')
}

function openProjects(remember = true) {
  resetProjectForm()
  selectedProjectId.value = null
  projectMessage.value = ''
  setCurrentView('projects', { remember })
  void loadDashboard()
}

function openProjectDetail(project: Project, remember = true) {
  selectedProjectId.value = project.id
  projectMessage.value = ''
  projectShareMessage.value = ''
  resetProjectShareForm()
  setCurrentView('project-detail', { remember })
}

function openCreateProject() {
  resetProjectForm()
  selectedProjectId.value = null
  projectMessage.value = ''
  setCurrentView('project-create')
}

function openEditProject(project: Project) {
  selectedProjectId.value = project.id
  resetProjectForm(project)
  projectMessage.value = ''
  setCurrentView('project-edit', { remember: false })
}

function openDeleteProject(project: Project) {
  selectedProjectId.value = project.id
  projectMessage.value = ''
  setCurrentView('project-delete')
}

function taskPayload() {
  const title = taskForm.value.title.trim()
  if (!title) {
    taskMessage.value = 'El titulo es obligatorio.'
    return null
  }

  return {
    title,
    description: taskForm.value.description.trim(),
    priority: taskForm.value.priority,
    status: taskForm.value.status,
    due_date: taskForm.value.due_date || null,
    project: taskForm.value.project ? Number(taskForm.value.project) : null,
  }
}

function projectPayload() {
  const name = projectForm.value.name.trim()
  if (!name) {
    projectMessage.value = 'El nombre del proyecto es obligatorio.'
    return null
  }

  return {
    name,
    description: projectForm.value.description.trim(),
    start_date: projectForm.value.start_date || null,
    end_date: projectForm.value.end_date || null,
  }
}

async function submitCreateTask() {
  taskMessage.value = ''
  const payload = taskPayload()
  if (!payload) return

  taskSaving.value = true
  try {
    const createdTask = await apiRequest<Task>('/tasks/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    tasks.value = [createdTask, ...tasks.value.filter((task) => task.id !== createdTask.id)]
    resetTaskForm()
    setCurrentView('tasks', { remember: false })
  } catch (error) {
    taskMessage.value = error instanceof Error ? error.message : 'No se pudo crear la tarea.'
  } finally {
    taskSaving.value = false
  }
}

async function submitEditTask() {
  taskMessage.value = ''
  const task = selectedTask.value
  const payload = taskPayload()
  if (!task || !payload) return

  taskSaving.value = true
  try {
    const updatedTask = await apiRequest<Task>(`/tasks/${task.id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    tasks.value = tasks.value.map((item) => (item.id === updatedTask.id ? updatedTask : item))
    selectedTaskId.value = updatedTask.id
    resetTaskForm(updatedTask)
    setCurrentView('task-detail', { remember: false })
  } catch (error) {
    taskMessage.value = error instanceof Error ? error.message : 'No se pudo guardar la tarea.'
  } finally {
    taskSaving.value = false
  }
}

async function confirmDeleteTask() {
  taskMessage.value = ''
  const task = selectedTask.value
  if (!task) return

  taskSaving.value = true
  try {
    await apiRequest<null>(`/tasks/${task.id}/`, { method: 'DELETE' })
    tasks.value = tasks.value.filter((item) => item.id !== task.id)
    selectedTaskId.value = null
    setCurrentView('tasks', { remember: false })
  } catch (error) {
    taskMessage.value = error instanceof Error ? error.message : 'No se pudo eliminar la tarea.'
  } finally {
    taskSaving.value = false
  }
}

async function submitCreateProject() {
  projectMessage.value = ''
  const payload = projectPayload()
  if (!payload) return

  projectSaving.value = true
  try {
    const createdProject = await apiRequest<Project>('/projects/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    projects.value = [createdProject, ...projects.value.filter((project) => project.id !== createdProject.id)]
    resetProjectForm()
    setCurrentView('projects', { remember: false })
  } catch (error) {
    projectMessage.value = error instanceof Error ? error.message : 'No se pudo crear el proyecto.'
  } finally {
    projectSaving.value = false
  }
}

async function submitEditProject() {
  projectMessage.value = ''
  const project = selectedProject.value
  const payload = projectPayload()
  if (!project || !payload) return

  projectSaving.value = true
  try {
    const updatedProject = await apiRequest<Project>(`/projects/${project.id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    projects.value = projects.value.map((item) => (item.id === updatedProject.id ? updatedProject : item))
    selectedProjectId.value = updatedProject.id
    resetProjectForm(updatedProject)
    setCurrentView('project-detail', { remember: false })
  } catch (error) {
    projectMessage.value = error instanceof Error ? error.message : 'No se pudo guardar el proyecto.'
  } finally {
    projectSaving.value = false
  }
}

async function confirmDeleteProject() {
  projectMessage.value = ''
  const project = selectedProject.value
  if (!project) return

  projectSaving.value = true
  try {
    await apiRequest<null>(`/projects/${project.id}/`, { method: 'DELETE' })
    projects.value = projects.value.filter((item) => item.id !== project.id)
    tasks.value = tasks.value.map((task) => (task.project === project.id ? { ...task, project: null } : task))
    selectedProjectId.value = null
    setCurrentView('projects', { remember: false })
  } catch (error) {
    projectMessage.value = error instanceof Error ? error.message : 'No se pudo eliminar el proyecto.'
  } finally {
    projectSaving.value = false
  }
}

async function shareTask() {
  taskShareMessage.value = ''
  const task = selectedTask.value
  const userIdentifier = taskShareForm.value.userIdentifier.trim()
  if (!task || !userIdentifier) {
    taskShareMessage.value = 'Indica el usuario o correo con el que quieres compartir.'
    return
  }

  shareLoading.value = true
  try {
    const collaboration = await apiRequest<Collaboration>('/collaborations/', {
      method: 'POST',
      body: JSON.stringify({
        user_identifier: userIdentifier,
        resource_type: 'TASK',
        task: task.id,
        role: taskShareForm.value.role,
      }),
    })
    collaborations.value = [
      collaboration,
      ...collaborations.value.filter((item) => item.id !== collaboration.id),
    ]
    resetTaskShareForm()
    taskShareMessage.value = 'Invitacion de colaboracion enviada correctamente.'
  } catch (error) {
    taskShareMessage.value = error instanceof Error ? error.message : 'No se pudo invitar al colaborador.'
  } finally {
    shareLoading.value = false
  }
}

async function shareProject() {
  projectShareMessage.value = ''
  const project = selectedProject.value
  const userIdentifier = projectShareForm.value.userIdentifier.trim()
  if (!project || !userIdentifier) {
    projectShareMessage.value = 'Indica el usuario o correo con el que quieres compartir.'
    return
  }

  shareLoading.value = true
  try {
    const collaboration = await apiRequest<Collaboration>('/collaborations/', {
      method: 'POST',
      body: JSON.stringify({
        user_identifier: userIdentifier,
        resource_type: 'PROJECT',
        project: project.id,
        role: projectShareForm.value.role,
      }),
    })
    collaborations.value = [
      collaboration,
      ...collaborations.value.filter((item) => item.id !== collaboration.id),
    ]
    resetProjectShareForm()
    projectShareMessage.value = 'Invitacion de colaboracion enviada correctamente.'
  } catch (error) {
    projectShareMessage.value = error instanceof Error ? error.message : 'No se pudo invitar al colaborador.'
  } finally {
    shareLoading.value = false
  }
}

async function submitEditProfile() {
  editProfileMessage.value = ''

  const profilePayload: Partial<Pick<UserProfile, 'username' | 'email'>> = {}
  const username = editProfileForm.value.username.trim()
  const email = editProfileForm.value.email.trim()
  const oldPassword = editProfileForm.value.oldPassword
  const password = editProfileForm.value.password

  if (username) profilePayload.username = username
  if (email) profilePayload.email = email

  const wantsPasswordChange = Boolean(oldPassword || password)
  if (wantsPasswordChange && (!oldPassword || !password)) {
    editProfileMessage.value = 'Para cambiar la contrasena, rellena la contrasena actual y la nueva.'
    return
  }

  profileSaving.value = true
  try {
    if (Object.keys(profilePayload).length) {
      profile.value = await apiRequest<UserProfile>('/auth/profile/', {
        method: 'PATCH',
        body: JSON.stringify(profilePayload),
      })
    }

    if (wantsPasswordChange) {
      await apiRequest('/auth/change-password/', {
        method: 'POST',
        body: JSON.stringify({
          old_password: oldPassword,
          password,
        }),
      })
    }

    resetEditProfileForm()
    setCurrentView('profile', { remember: false })
  } catch (error) {
    editProfileMessage.value =
      error instanceof Error ? error.message : 'No se pudieron guardar los cambios.'
  } finally {
    profileSaving.value = false
  }
}

function clearSessionState() {
  clearTokens()
  profile.value = null
  tasks.value = []
  projects.value = []
  dashboard.value = null
  calendar.value = null
  collaborations.value = []
  users.value = []
  selectedTaskId.value = null
  selectedProjectId.value = null
  resetEditProfileForm()
  resetTaskForm()
  resetProjectForm()
  resetTaskShareForm()
  resetProjectShareForm()
  clearAuthForms()
  setCurrentView('auth', { clearHistory: true })
  authMode.value = 'login'
  authMessage.value = ''
  dashboardMessage.value = ''
  editProfileMessage.value = ''
  taskMessage.value = ''
  projectMessage.value = ''
  taskShareMessage.value = ''
  projectShareMessage.value = ''
  calendarMessage.value = ''
}

async function logout() {
  const refresh = refreshToken.value

  try {
    if (accessToken.value && refresh) {
      await apiRequest('/auth/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      })
    }
  } catch {
    // Aunque el token haya expirado o el servidor no responda, la sesion local debe cerrarse.
  } finally {
    clearSessionState()
  }
}

function projectNameForTask(task: Task | null) {
  if (!task?.project) return 'Sin proyecto'
  return projects.value.find((project) => project.id === task.project)?.name || 'Sin proyecto'
}

function isResourceOwner(resource: { owner?: UserProfile } | null) {
  return Boolean(profile.value?.id && resource?.owner?.id === profile.value.id)
}

function canEditResource(resource: { can_edit?: boolean } | null) {
  return Boolean(resource?.can_edit)
}

function canDeleteResource(resource: { is_owner?: boolean } | null) {
  return Boolean(resource?.is_owner)
}

function accessMessage(resource: { collaboration_role?: string | null; can_edit?: boolean } | null, label: string) {
  if (!resource?.collaboration_role || resource.collaboration_role === 'OWNER') {
    return `Eres propietario de ${label}. Puedes editar e invitar colaboradores.`
  }
  if (resource.can_edit) {
    return `Colaborador: puedes editar y participar en ${label}.`
  }
  return `Colaborador: puedes consultar ${label}.`
}

function toIsoDate(date: Date) {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localDate.toISOString().slice(0, 10)
}

function formatDate(value: string | null) {
  if (!value) return 'Sin fecha'
  const date = new Date(`${value}T00:00:00`)
  const today = new Date()
  const tomorrow = new Date()
  tomorrow.setDate(today.getDate() + 1)
  if (date.toDateString() === today.toDateString()) return 'Hoy'
  if (date.toDateString() === tomorrow.toDateString()) return 'Manana'
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short' }).format(date)
}

function statusLabel(status: Task['status']) {
  const labels = {
    PENDING: 'PENDIENTE',
    IN_PROGRESS: 'EN PROGRESO',
    COMPLETED: 'COMPLETADA',
    CANCELLED: 'CANCELADA',
  }
  return labels[status]
}

function statusClass(status: Task['status']) {
  const classes = {
    PENDING: 'status-pending',
    IN_PROGRESS: 'status-progress',
    COMPLETED: 'status-completed',
    CANCELLED: 'status-cancelled',
  }
  return classes[status]
}

onMounted(() => {
  if (accessToken.value) {
    setCurrentView('dashboard', { clearHistory: true })
    void loadDashboard()
  }
})
</script>

<template>
  <main class="app-shell" :class="{ 'has-back-button': showBackButton }">
    <BotonVolver v-if="showBackButton" @click="goBack" />

    <PantallaRegistro
      v-if="currentView === 'auth' && authMode === 'register'"
      :register-form="registerForm"
      :loading="loading"
      :message="authMessage"
      @submit-register="submitRegister"
      @switch-mode="switchAuthMode"
    />

    <PantallaIniciarSesion
      v-else-if="currentView === 'auth'"
      :login-form="loginForm"
      :loading="loading"
      :message="authMessage"
      @submit-login="submitLogin"
      @switch-mode="switchAuthMode"
    />

    <PantallaInicio
      v-else-if="currentView === 'dashboard'"
      :display-name="displayName"
      :initials="initials"
      :pending-tasks="pendingTasks"
      :completed-tasks="completedTasks"
      :active-projects="activeProjects"
      :effective-minutes="effectiveMinutes"
      :upcoming-tasks="upcomingTasks"
      :recent-activity="recentActivity"
      :dashboard-loading="dashboardLoading"
      :dashboard-message="dashboardMessage"
      @open-profile="openProfile"
      @navigate="handleNavigation"
    />

    <PantallaCalendario
      v-else-if="currentView === 'calendar'"
      :calendar="calendar"
      :selected-date="calendarDate"
      :initials="initials"
      :loading="calendarLoading"
      :message="calendarMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @change-month="changeCalendarMonth"
      @open-item="openCalendarItem"
    />

    <PantallaMisTareas
      v-else-if="currentView === 'tasks'"
      :tasks="tasks"
      :initials="initials"
      :loading="dashboardLoading"
      :message="dashboardMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @create-task="openCreateTask"
      @view-task="openTaskDetail"
      @edit-task="openEditTask"
      @delete-task="openDeleteTask"
    />

    <PantallaTarea
      v-else-if="currentView === 'task-detail'"
      :task="selectedTask"
      :project-name="projectNameForTask(selectedTask)"
      :initials="initials"
      :can-share="canShareSelectedTask"
      :can-edit="canEditResource(selectedTask)"
      :can-delete="canDeleteResource(selectedTask)"
      :access-message="accessMessage(selectedTask, 'esta tarea')"
      :share-form="taskShareForm"
      :share-loading="shareLoading"
      :share-message="taskShareMessage"
      :collaborations="selectedTaskCollaborations"
      :users="users"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @edit-task="openEditTask"
      @delete-task="openDeleteTask"
      @share-task="shareTask"
    />

    <PantallaCrearTarea
      v-else-if="currentView === 'task-create'"
      :form="taskForm"
      :projects="projects"
      :initials="initials"
      :loading="taskSaving"
      :message="taskMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @submit="submitCreateTask"
      @cancel="openTasks(false)"
    />

    <PantallaEditarTarea
      v-else-if="currentView === 'task-edit'"
      :form="taskForm"
      :projects="projects"
      :initials="initials"
      :loading="taskSaving"
      :message="taskMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @submit="submitEditTask"
      @cancel="selectedTask ? openTaskDetail(selectedTask, false) : openTasks(false)"
    />

    <PantallaEliminarTarea
      v-else-if="currentView === 'task-delete'"
      :task="selectedTask"
      :tasks="tasks"
      :initials="initials"
      :loading="taskSaving"
      :message="taskMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @cancel="openTasks(false)"
      @confirm="confirmDeleteTask"
    />

    <PantallaMisProyectos
      v-else-if="currentView === 'projects'"
      :projects="projects"
      :initials="initials"
      :loading="dashboardLoading"
      :message="dashboardMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @create-project="openCreateProject"
      @view-project="openProjectDetail"
      @edit-project="openEditProject"
      @delete-project="openDeleteProject"
    />

    <PantallaProyecto
      v-else-if="currentView === 'project-detail'"
      :project="selectedProject"
      :tasks="selectedProjectTasks"
      :initials="initials"
      :can-share="canShareSelectedProject"
      :can-edit="canEditResource(selectedProject)"
      :can-delete="canDeleteResource(selectedProject)"
      :access-message="accessMessage(selectedProject, 'este proyecto')"
      :share-form="projectShareForm"
      :share-loading="shareLoading"
      :share-message="projectShareMessage"
      :collaborations="selectedProjectCollaborations"
      :users="users"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @edit-project="openEditProject"
      @delete-project="openDeleteProject"
      @view-task="openTaskDetail"
      @edit-task="openEditTask"
      @delete-task="openDeleteTask"
      @share-project="shareProject"
    />

    <PantallaCrearProyecto
      v-else-if="currentView === 'project-create'"
      :form="projectForm"
      :initials="initials"
      :loading="projectSaving"
      :message="projectMessage"
      mode="create"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @submit="submitCreateProject"
      @cancel="openProjects(false)"
    />

    <PantallaEditarProyecto
      v-else-if="currentView === 'project-edit'"
      :form="projectForm"
      :initials="initials"
      :loading="projectSaving"
      :message="projectMessage"
      mode="edit"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @submit="submitEditProject"
      @cancel="selectedProject ? openProjectDetail(selectedProject, false) : openProjects(false)"
    />

    <PantallaEliminarProyecto
      v-else-if="currentView === 'project-delete'"
      :project="selectedProject"
      :projects="projects"
      :initials="initials"
      :loading="projectSaving"
      :message="projectMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @cancel="openProjects(false)"
      @confirm="confirmDeleteProject"
    />

    <PantallaPerfil
      v-else-if="currentView === 'profile'"
      :display-name="profileDisplayName"
      :username="profileUsername"
      :email="profileEmail"
      @go-home="openDashboard"
      @navigate="handleNavigation"
      @edit-profile="openEditProfile"
      @logout="logout"
    />

    <PantallaEditarPerfil
      v-else
      :display-name="profileDisplayName"
      :username="profileUsername"
      :email="profileEmail"
      :form="editProfileForm"
      :loading="profileSaving"
      :message="editProfileMessage"
      @submit="submitEditProfile"
      @cancel="cancelEditProfile"
      @go-home="openDashboard"
      @navigate="handleNavigation"
      @logout="logout"
    />

    <footer class="app-footer">
      Autor: Jaime Martínez Benítez&nbsp;&nbsp; TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
    </footer>
  </main>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  min-width: 320px;
  background: #f6f6f7;
  color: #050505;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

:global(button),
:global(input),
:global(textarea),
:global(select) {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
}

.app-shell.has-back-button :global(.profile-content),
.app-shell.has-back-button :global(.tasks-content),
.app-shell.has-back-button :global(.task-content),
.app-shell.has-back-button :global(.task-form-content),
.app-shell.has-back-button :global(.delete-content),
.app-shell.has-back-button :global(.projects-content),
.app-shell.has-back-button :global(.project-content),
.app-shell.has-back-button :global(.project-form-content) {
  padding-top: 94px;
}


.app-footer {
  position: fixed;
  right: 18px;
  bottom: 12px;
  left: 18px;
  z-index: 20;
  padding: 4px 10px;
  color: #555967;
  background: rgb(255 255 255 / 82%);
  border-radius: 999px;
  text-align: center;
  font-size: 0.72rem;
  line-height: 1.35;
  pointer-events: none;
}

@media (max-width: 760px) {
  .app-footer {
    right: 10px;
    bottom: 8px;
    left: 10px;
    border-radius: 10px;
    font-size: 0.66rem;
  }
}
</style>
