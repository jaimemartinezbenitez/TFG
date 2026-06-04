<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "VentanaPrincipal.vue"
Descripcion: Coordina el estado, navegación y comunicación con la API.
-->

<script setup lang="ts">
import BotonVolver from './BotonVolver.vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Pantalla5217 from './Pantalla5217.vue'
import Pantalla5217Descanso from './Pantalla5217Descanso.vue'
import PantallaCalendario from './PantallaCalendario.vue'
import PantallaCrearProyecto from './PantallaCrearProyecto.vue'
import PantallaCrearTarea from './PantallaCrearTarea.vue'
import PantallaEditarPerfil from './PantallaEditarPerfil.vue'
import PantallaEditarProyecto from './PantallaEditarProyecto.vue'
import PantallaEditarTarea from './PantallaEditarTarea.vue'
import PantallaEliminarProyecto from './PantallaEliminarProyecto.vue'
import PantallaEliminarTarea from './PantallaEliminarTarea.vue'
import PantallaExportarDatos from './PantallaExportarDatos.vue'
import PantallaInicio from './PantallaInicio.vue'
import PantallaIniciarSesion from './PantallaIniciarSesion.vue'
import PantallaLogros from './PantallaLogros.vue'
import PantallaMisProyectos from './PantallaMisProyectos.vue'
import PantallaMisTareas from './PantallaMisTareas.vue'
import PantallaPerfil from './PantallaPerfil.vue'
import PantallaPomodoro from './PantallaPomodoro.vue'
import PantallaPomodoroDescanso from './PantallaPomodoroDescanso.vue'
import PantallaProyecto from './PantallaProyecto.vue'
import PantallaRegistro from './PantallaRegistro.vue'
import PantallaRecuperarContrasena from './PantallaRecuperarContrasena.vue'
import PantallaEstadisticas from './PantallaEstadisticas.vue'
import PantallaResumen5217 from './PantallaResumen5217.vue'
import PantallaResumenPomodoro from './PantallaResumenPomodoro.vue'
import PantallaTarea from './PantallaTarea.vue'
import PantallaTecnicas from './PantallaTecnicas.vue'
import PantallaTimeBlocking from './PantallaTimeBlocking.vue'
import { useRoute, useRouter } from 'vue-router'
import type {
  Achievement,
  ActivityItem,
  AuthMode,
  CalendarData,
  CalendarItem,
  Collaboration,
  DashboardData,
  DashboardTaskItem,
  DeleteAccountForm,
  EditProfileForm,
  ExportForm,
  LoginForm,
  Notification,
  PasswordResetForm,
  ProductivitySession,
  ProductivityTechnique,
  Project,
  ProjectForm,
  RegisterForm,
  ShareForm,
  StatisticsPeriod,
  Task,
  TechniqueTimerState,
  TimeBlock,
  TaskForm,
  UserProfile,
} from './types'

const API_BASE = '/api'

const route = useRoute()
const router = useRouter()

type NamedRouteLocation = { name: string; params?: { id?: number | string } }

type AppView =
  | 'auth'
  | 'dashboard'
  | 'profile'
  | 'edit-profile'
  | 'calendar'
  | 'statistics'
  | 'achievements'
  | 'export'
  | 'techniques'
  | 'technique-pomodoro'
  | 'technique-pomodoro-break'
  | 'technique-pomodoro-summary'
  | 'technique-5217'
  | 'technique-5217-break'
  | 'technique-5217-summary'
  | 'technique-time-blocking'
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
const authMode = ref<AuthMode>('login')
const loading = ref(false)
const dashboardLoading = ref(false)
const achievementLoading = ref(false)
const calendarLoading = ref(false)
const notificationLoading = ref(false)
const authMessage = ref('')
const dashboardMessage = ref('')
const achievementMessage = ref('')
const calendarMessage = ref('')
const exportMessage = ref('')
const editProfileMessage = ref('')
const deleteAccountMessage = ref('')
const profileSaving = ref(false)
const accountDeleting = ref(false)
const exportLoading = ref(false)
const taskMessage = ref('')
const taskSaving = ref(false)
const projectMessage = ref('')
const projectSaving = ref(false)
const taskShareMessage = ref('')
const projectShareMessage = ref('')
const shareLoading = ref(false)
const collaborationLoading = ref(false)
const techniqueLoading = ref(false)
const techniqueSaving = ref(false)
const techniqueMessage = ref('')
const calendarDate = ref(toIsoDate(new Date()))
const statisticsPeriod = ref<StatisticsPeriod>('week')
const statisticsDate = ref(toIsoDate(new Date()))
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

const passwordResetForm = ref<PasswordResetForm>({
  email: '',
  token: '',
  password: '',
  confirmPassword: '',
})

const editProfileForm = ref<EditProfileForm>({
  username: '',
  email: '',
  oldPassword: '',
  password: '',
})

const deleteAccountForm = ref<DeleteAccountForm>({
  password: '',
})

const taskForm = ref<TaskForm>(emptyTaskForm())
const projectForm = ref<ProjectForm>(emptyProjectForm())
const exportForm = ref<ExportForm>(emptyExportForm())
const taskShareForm = ref<ShareForm>(emptyShareForm())
const projectShareForm = ref<ShareForm>(emptyShareForm())

const profile = ref<UserProfile | null>(null)
const tasks = ref<Task[]>([])
const projects = ref<Project[]>([])
const dashboard = ref<DashboardData | null>(null)
const calendar = ref<CalendarData | null>(null)
const collaborations = ref<Collaboration[]>([])
const notifications = ref<Notification[]>([])
const users = ref<UserProfile[]>([])
const productivitySessions = ref<ProductivitySession[]>([])
const achievements = ref<Achievement[]>([])
const activeProductivitySession = ref<ProductivitySession | null>(null)
const techniqueTimer = ref<TechniqueTimerState>(emptyTechniqueTimer('POMODORO'))
const timeBlocks = ref<TimeBlock[]>(defaultTimeBlocks())
const syncingRouterRoute = ref(false)
let techniqueInterval: ReturnType<typeof window.setInterval> | null = null

function routeParamId(value: unknown) {
  const rawValue = Array.isArray(value) ? value[0] : value
  const id = Number(rawValue)
  return Number.isInteger(id) && id > 0 ? id : null
}

function routeTargetFromName() {
  const name = String(route.name || 'login')
  const taskId = routeParamId(route.params.id)
  const projectId = routeParamId(route.params.id)

  if (name === 'register') return { view: 'auth' as AppView, authMode: 'register' as AuthMode }
  if (name === 'login') return { view: 'auth' as AppView, authMode: 'login' as AuthMode }
  if (name === 'password-reset') return { view: 'auth' as AppView, authMode: 'password-reset' as AuthMode }
  if (name === 'task-detail') return { view: 'task-detail' as AppView, taskId }
  if (name === 'task-edit') return { view: 'task-edit' as AppView, taskId }
  if (name === 'task-delete') return { view: 'task-delete' as AppView, taskId }
  if (name === 'project-detail') return { view: 'project-detail' as AppView, projectId }
  if (name === 'project-edit') return { view: 'project-edit' as AppView, projectId }
  if (name === 'project-delete') return { view: 'project-delete' as AppView, projectId }
  return { view: name as AppView }
}

function routerLocationForCurrentView(): NamedRouteLocation {
  if (currentView.value === 'auth') {
    if (authMode.value === 'register') return { name: 'register' }
    if (authMode.value === 'password-reset') return { name: 'password-reset' }
    return { name: 'login' }
  }
  if (currentView.value === 'task-detail' && selectedTaskId.value) {
    return { name: 'task-detail', params: { id: selectedTaskId.value } }
  }
  if (currentView.value === 'task-edit' && selectedTaskId.value) {
    return { name: 'task-edit', params: { id: selectedTaskId.value } }
  }
  if (currentView.value === 'task-delete' && selectedTaskId.value) {
    return { name: 'task-delete', params: { id: selectedTaskId.value } }
  }
  if (currentView.value === 'project-detail' && selectedProjectId.value) {
    return { name: 'project-detail', params: { id: selectedProjectId.value } }
  }
  if (currentView.value === 'project-edit' && selectedProjectId.value) {
    return { name: 'project-edit', params: { id: selectedProjectId.value } }
  }
  if (currentView.value === 'project-delete' && selectedProjectId.value) {
    return { name: 'project-delete', params: { id: selectedProjectId.value } }
  }
  return { name: currentView.value }
}

function sameRouteLocation(location: NamedRouteLocation) {
  if (route.name !== location.name) return false
  const expectedId = location.params?.id ? Number(location.params.id) : null
  const routeId = routeParamId(route.params.id)
  return expectedId ? expectedId === routeId : routeId === null
}

async function syncRouterUrl(options: { replace?: boolean } = {}) {
  if (syncingRouterRoute.value) return
  const location = routerLocationForCurrentView()
  if (sameRouteLocation(location)) return

  syncingRouterRoute.value = true
  try {
    if (options.replace) {
      await router.replace(location)
      return
    }
    await router.push(location)
  } finally {
    syncingRouterRoute.value = false
  }
}

async function loadDataForCurrentRoute() {
  if (!accessToken.value || currentView.value === 'auth') return

  if (currentView.value === 'achievements') {
    await loadAchievements()
    return
  }

  if (
    [
      'techniques',
      'technique-pomodoro',
      'technique-pomodoro-break',
      'technique-pomodoro-summary',
      'technique-5217',
      'technique-5217-break',
      'technique-5217-summary',
      'technique-time-blocking',
    ].includes(currentView.value)
  ) {
    await loadProductivitySessions()
  }

  await loadDashboard()

  if (currentView.value === 'calendar') {
    await loadCalendar()
  }
  if (currentView.value === 'task-edit' && selectedTask.value) {
    resetTaskForm(selectedTask.value)
  }
  if (currentView.value === 'project-edit' && selectedProject.value) {
    resetProjectForm(selectedProject.value)
  }
}

async function applyRouteToState() {
  const target = routeTargetFromName()

  if (accessToken.value && target.view === 'auth') {
    await router.replace({ name: 'dashboard' })
    return
  }

  if (!accessToken.value && target.view !== 'auth') {
    await router.replace({ name: 'login' })
    return
  }

  syncingRouterRoute.value = true
  navigationHistory.value = []
  if (target.authMode) authMode.value = target.authMode
  selectedTaskId.value = target.taskId ?? null
  selectedProjectId.value = target.projectId ?? null
  currentView.value = target.view
  syncingRouterRoute.value = false
  await loadDataForCurrentRoute()
}


function emptyTaskForm(): TaskForm {
  return {
    title: '',
    description: '',
    priority: 'HIGH',
    status: 'PENDING',
    due_date: '',
    project: '',
    collaboratorIdentifier: '',
    collaboratorRole: 'READER',
  }
}

function emptyProjectForm(): ProjectForm {
  return {
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    collaboratorIdentifier: '',
    collaboratorRole: 'READER',
  }
}

function emptyExportForm(): ExportForm {
  return {
    deadline: '',
    project: '',
    format: 'csv',
  }
}

function emptyShareForm(): ShareForm {
  return {
    userIdentifier: '',
    role: 'READER',
  }
}

function emptyTechniqueTimer(technique: ProductivityTechnique): TechniqueTimerState {
  const isPomodoro = technique === 'POMODORO'
  const workMinutes = isPomodoro ? 25 : 52
  const breakMinutes = isPomodoro ? 5 : 17
  return {
    technique,
    phase: 'focus',
    workMinutes,
    breakMinutes,
    targetCycles: 4,
    currentCycle: 1,
    completedCycles: 0,
    remainingSeconds: workMinutes * 60,
    effectiveSeconds: 0,
    breakSeconds: 0,
    isRunning: false,
  }
}

function defaultTimeBlocks(): TimeBlock[] {
  return []
}

function resetTechniqueState() {
  clearTechniqueInterval()
  activeProductivitySession.value = null
  techniqueTimer.value = emptyTechniqueTimer('POMODORO')
  timeBlocks.value = defaultTimeBlocks()
  techniqueMessage.value = ''
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

function resetPasswordResetForm() {
  passwordResetForm.value = {
    email: '',
    token: '',
    password: '',
    confirmPassword: '',
  }
}

function clearAuthForms() {
  resetRegisterForm()
  resetLoginForm()
  resetPasswordResetForm()
}

function resetEditProfileForm() {
  editProfileForm.value = {
    username: '',
    email: '',
    oldPassword: '',
    password: '',
  }
}

function resetDeleteAccountForm() {
  deleteAccountForm.value = {
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
        collaboratorIdentifier: '',
        collaboratorRole: 'READER',
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
        collaboratorIdentifier: '',
        collaboratorRole: 'READER',
      }
    : emptyProjectForm()
}

function resetTaskShareForm() {
  taskShareForm.value = emptyShareForm()
}

function resetProjectShareForm() {
  projectShareForm.value = emptyShareForm()
}

function resetExportForm() {
  exportForm.value = emptyExportForm()
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
const pendingCollaborations = computed(() =>
  collaborations.value.filter(
    (collaboration) => collaboration.user === profile.value?.id && collaboration.status === 'PENDING',
  ),
)
const canShareSelectedTask = computed(() => Boolean(selectedTask.value?.can_invite_collaborators))
const canShareSelectedProject = computed(() => Boolean(selectedProject.value?.can_invite_collaborators))

const pendingTasks = computed(() => tasks.value.filter((task) => task.status !== 'COMPLETED').length)
const completedTasks = computed(() => tasks.value.filter((task) => task.status === 'COMPLETED').length)
const activeProjects = computed(() => projects.value.length)
const effectiveMinutes = computed(() => dashboard.value?.metric?.effective_minutes || 0)

const upcomingTasks = computed<DashboardTaskItem[]>(() => {
  const today = toIsoDate(new Date())
  return tasks.value
    .filter((task) => {
      const dueDate = task.due_date
      return dueDate !== null && dueDate >= today && ['PENDING', 'IN_PROGRESS'].includes(task.status)
    })
    .sort((a, b) => (a.due_date || '').localeCompare(b.due_date || ''))
    .slice(0, 3)
    .map((task) => ({
      id: task.id,
      title: task.title,
      dateLabel: formatDate(task.due_date),
    }))
})

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
    'calendar',
    'export',
    'techniques',
    'statistics',
    'achievements',
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
  void syncRouterUrl({ replace: options.clearHistory })
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
  headers.set('Accept', 'application/json')
  if (!headers.has('Content-Type') && options.body) headers.set('Content-Type', 'application/json')
  if (accessToken.value) headers.set('Authorization', `Bearer ${accessToken.value}`)

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const text = await response.text()
  const contentType = response.headers.get('content-type') || ''

  if (text && !contentType.includes('application/json')) {
    throw new Error(
      response.ok
        ? 'La API no devolvio JSON. Revisa que el backend de Django este arrancado.'
        : `La API devolvio una pagina HTML (${response.status}). Revisa la consola del backend de Django.`,
    )
  }

  let payload: unknown = null
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      throw new Error('La API devolvio una respuesta no valida.')
    }
  }

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

async function submitPasswordResetRequest() {
  authMessage.value = ''
  loading.value = true
  try {
    const response = await apiRequest<{ detail?: string; token?: string; expires_at?: string }>('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email: passwordResetForm.value.email }),
    })
    if (response.token) {
      passwordResetForm.value.token = response.token
      authMessage.value = `${response.detail || 'Token generado para entorno local.'} Token: ${response.token}`
      return
    }
    authMessage.value = response.detail || 'Token de recuperacion generado.'
  } catch (error) {
    authMessage.value = error instanceof Error ? error.message : 'No se pudo solicitar la recuperacion.'
  } finally {
    loading.value = false
  }
}

async function submitPasswordResetConfirm() {
  authMessage.value = ''
  if (passwordResetForm.value.password !== passwordResetForm.value.confirmPassword) {
    authMessage.value = 'Las contrasenas no coinciden.'
    return
  }

  loading.value = true
  try {
    await apiRequest('/auth/password-reset/confirm/', {
      method: 'POST',
      body: JSON.stringify({
        token: passwordResetForm.value.token,
        password: passwordResetForm.value.password,
      }),
    })
    clearAuthForms()
    authMode.value = 'login'
    authMessage.value = 'Contrasena actualizada. Ya puedes iniciar sesion.'
    void syncRouterUrl({ replace: true })
  } catch (error) {
    authMessage.value = error instanceof Error ? error.message : 'No se pudo cambiar la contrasena.'
  } finally {
    loading.value = false
  }
}

async function loadDashboard() {
  if (!accessToken.value) return
  dashboardLoading.value = true
  dashboardMessage.value = ''
  try {
    const [
      profileData,
      taskData,
      projectData,
      dashboardData,
      collaborationData,
      notificationData,
      userData,
      productivitySessionData,
      achievementData,
    ] = await Promise.all([
      apiRequest<UserProfile>('/auth/profile/'),
      apiRequest<Task[]>('/tasks/'),
      apiRequest<Project[]>('/projects/'),
      apiRequest<DashboardData>(`/statistics/dashboard/?view=${statisticsPeriod.value}&date=${statisticsDate.value}`),
      apiRequest<Collaboration[]>('/collaborations/'),
      apiRequest<Notification[]>('/notifications/'),
      apiRequest<UserProfile[]>('/users/'),
      apiRequest<ProductivitySession[]>('/productivity-sessions/'),
      apiRequest<Achievement[]>('/achievements/'),
    ])
    profile.value = profileData
    tasks.value = taskData
    projects.value = projectData
    dashboard.value = dashboardData
    collaborations.value = collaborationData
    notifications.value = notificationData
    users.value = userData
    productivitySessions.value = productivitySessionData
    achievements.value = achievementData
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
  void syncRouterUrl({ replace: true })
}

function handleNavigation(section: string) {
  if (section === 'inicio') openDashboard()
  if (section === 'tareas') openTasks()
  if (section === 'proyecto') openProjects()
  if (section === 'calendario') openCalendar()
  if (section === 'tecnicas') openTechniques()
  if (section === 'estadisticas') openStatistics()
  if (section === 'logros') openAchievements()
  if (section === 'exportar') openExport()
}

async function markNotificationRead(notification: Notification) {
  notificationLoading.value = true
  dashboardMessage.value = ''
  try {
    const updated = await apiRequest<Notification>(`/notifications/${notification.id}/mark_read/`, {
      method: 'POST',
    })
    notifications.value = notifications.value.map((item) => (item.id === updated.id ? updated : item))
  } catch (error) {
    dashboardMessage.value = error instanceof Error ? error.message : 'No se pudo actualizar la notificacion.'
  } finally {
    notificationLoading.value = false
  }
}

function openProfile() {
  resetDeleteAccountForm()
  deleteAccountMessage.value = ''
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
  resetDeleteAccountForm()
  resetTaskForm()
  resetProjectForm()
  resetTaskShareForm()
  resetProjectShareForm()
  taskMessage.value = ''
  projectMessage.value = ''
  taskShareMessage.value = ''
  projectShareMessage.value = ''
  calendarMessage.value = ''
  deleteAccountMessage.value = ''
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

function openStatistics() {
  dashboardMessage.value = ''
  setCurrentView('statistics')
  void loadDashboard()
}

async function loadAchievements() {
  if (!accessToken.value) return
  achievementLoading.value = true
  achievementMessage.value = ''
  try {
    achievements.value = await apiRequest<Achievement[]>('/achievements/')
  } catch (error) {
    achievementMessage.value = error instanceof Error ? error.message : 'No se pudieron cargar los logros.'
  } finally {
    achievementLoading.value = false
  }
}

function openAchievements() {
  achievementMessage.value = ''
  setCurrentView('achievements')
  void loadAchievements()
}

function openExport() {
  exportMessage.value = ''
  setCurrentView('export')
  void loadDashboard()
}

function projectTitleForId(projectId: number | null) {
  if (!projectId) return 'Sin proyecto'
  return projects.value.find((project) => project.id === projectId)?.name || 'Sin proyecto'
}

function exportFileBaseName() {
  const date = toIsoDate(new Date())
  const project = exportForm.value.project
    ? projects.value.find((item) => item.id === Number(exportForm.value.project))?.name || 'proyecto'
    : 'todos'
  return `concentraplus-${slug(project)}-${date}`
}

function slug(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'datos'
}

function filteredTasksForExport() {
  const deadline = exportForm.value.deadline
  const projectId = exportForm.value.project ? Number(exportForm.value.project) : null

  return tasks.value.filter((task) => {
    if (projectId && task.project !== projectId) return false
    if (deadline && task.due_date && task.due_date > deadline) return false
    return true
  })
}

function filteredProjectsForExport(exportedTasks = filteredTasksForExport()) {
  const projectId = exportForm.value.project ? Number(exportForm.value.project) : null
  if (projectId) return projects.value.filter((project) => project.id === projectId)

  const deadline = exportForm.value.deadline
  const taskProjectIds = new Set(exportedTasks.map((task) => task.project).filter((value): value is number => value !== null))
  return projects.value.filter((project) => {
    if (deadline && project.end_date && project.end_date > deadline) return false
    return !taskProjectIds.size || taskProjectIds.has(project.id) || !deadline
  })
}

function escapeCsv(value: unknown) {
  const text = String(value ?? '')
  return `"${text.replace(/"/g, '""')}"`
}

function downloadTextFile(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

async function downloadApiFile(path: string, filename: string) {
  const headers = new Headers()
  if (accessToken.value) headers.set('Authorization', `Bearer ${accessToken.value}`)
  const response = await fetch(`${API_BASE}${path}`, { headers })

  if (!response.ok) {
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      const payload = await response.json()
      throw new Error(extractError(payload))
    }
    throw new Error('No se pudo generar el archivo.')
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function exportQueryString() {
  const params = new URLSearchParams()
  if (exportForm.value.deadline) {
    params.set('start', '1970-01-01')
    params.set('end', exportForm.value.deadline)
  }
  if (exportForm.value.project) {
    params.set('project', exportForm.value.project)
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}

function downloadCsv() {
  const exportedTasks = filteredTasksForExport()
  const exportedProjects = filteredProjectsForExport(exportedTasks)
  const rows = [
    ['Tipo', 'Proyecto', 'Titulo', 'Descripcion', 'Estado', 'Prioridad', 'Fecha limite', 'Fecha inicio', 'Fecha fin'],
    ...exportedProjects.map((project) => [
      'Proyecto',
      project.name,
      project.name,
      project.description,
      `${project.progress_percentage ?? 0}%`,
      '',
      '',
      project.start_date || '',
      project.end_date || '',
    ]),
    ...exportedTasks.map((task) => [
      'Tarea',
      projectTitleForId(task.project),
      task.title,
      task.description,
      statusLabel(task.status),
      task.priority,
      task.due_date || '',
      task.created_at.slice(0, 10),
      task.updated_at.slice(0, 10),
    ]),
  ]
  const csv = rows.map((row) => row.map(escapeCsv).join(',')).join('\n')
  downloadTextFile(csv, `${exportFileBaseName()}.csv`, 'text/csv;charset=utf-8')
}

function escapeHtml(value: unknown) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function printableHtml() {
  const exportedTasks = filteredTasksForExport()
  const exportedProjects = filteredProjectsForExport(exportedTasks)
  const selectedProjectName = exportForm.value.project
    ? projectTitleForId(Number(exportForm.value.project))
    : 'Todos los proyectos'
  const deadline = exportForm.value.deadline || 'Sin fecha limite'

  const projectRows = exportedProjects
    .map(
      (project) => `
        <tr>
          <td>${escapeHtml(project.name)}</td>
          <td>${escapeHtml(project.description || 'Sin descripcion')}</td>
          <td>${escapeHtml(project.start_date || 'Sin fecha')}</td>
          <td>${escapeHtml(project.end_date || 'Sin fecha')}</td>
          <td>${escapeHtml(project.progress_percentage ?? 0)}%</td>
        </tr>`,
    )
    .join('')
  const taskRows = exportedTasks
    .map(
      (task) => `
        <tr>
          <td>${escapeHtml(task.title)}</td>
          <td>${escapeHtml(projectTitleForId(task.project))}</td>
          <td>${escapeHtml(statusLabel(task.status))}</td>
          <td>${escapeHtml(task.priority)}</td>
          <td>${escapeHtml(task.due_date || 'Sin fecha')}</td>
        </tr>`,
    )
    .join('')

  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Exportar datos</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #111; }
    h1 { margin: 0 0 8px; font-size: 30px; }
    h2 { margin-top: 28px; font-size: 20px; }
    p { margin: 4px 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { border: 1px solid #75ddcb; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f2fffb; }
    .meta { margin: 18px 0 24px; }
  </style>
</head>
<body>
  <h1>Exportar datos</h1>
  <div class="meta">
    <p><strong>Proyecto:</strong> ${escapeHtml(selectedProjectName)}</p>
    <p><strong>Fecha limite:</strong> ${escapeHtml(deadline)}</p>
    <p><strong>Generado:</strong> ${escapeHtml(new Intl.DateTimeFormat('es-ES').format(new Date()))}</p>
  </div>

  <h2>Proyectos</h2>
  <table>
    <thead><tr><th>Proyecto</th><th>Descripcion</th><th>Inicio</th><th>Fin</th><th>Progreso</th></tr></thead>
    <tbody>${projectRows || '<tr><td colspan="5">No hay proyectos para estos filtros.</td></tr>'}</tbody>
  </table>

  <h2>Tareas</h2>
  <table>
    <thead><tr><th>Tarea</th><th>Proyecto</th><th>Estado</th><th>Prioridad</th><th>Fecha limite</th></tr></thead>
    <tbody>${taskRows || '<tr><td colspan="5">No hay tareas para estos filtros.</td></tr>'}</tbody>
  </table>
</body>
</html>`
}

function downloadPdf() {
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    exportMessage.value = 'El navegador ha bloqueado la ventana de impresion.'
    return
  }
  printWindow.document.write(printableHtml())
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
}

async function submitExport() {
  exportMessage.value = ''
  exportLoading.value = true
  try {
    const format = exportForm.value.format
    await downloadApiFile(
      `/exports/${format}/${exportQueryString()}`,
      `${exportFileBaseName()}.${format}`,
    )
    exportMessage.value = 'Archivo generado correctamente.'
  } catch (error) {
    exportMessage.value = error instanceof Error ? error.message : 'No se pudo exportar la informacion.'
  } finally {
    exportLoading.value = false
  }
}

function changeStatisticsPeriod(period: StatisticsPeriod, date: string) {
  statisticsPeriod.value = period
  statisticsDate.value = date || toIsoDate(new Date())
  void loadDashboard()
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


async function loadProductivitySessions() {
  if (!accessToken.value) return
  try {
    productivitySessions.value = await apiRequest<ProductivitySession[]>('/productivity-sessions/')
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudieron cargar las sesiones.'
  }
}

function clearTechniqueInterval() {
  if (techniqueInterval !== null) {
    window.clearInterval(techniqueInterval)
    techniqueInterval = null
  }
}

function focusViewFor(technique: ProductivityTechnique): AppView {
  return technique === 'POMODORO' ? 'technique-pomodoro' : 'technique-5217'
}

function breakViewFor(technique: ProductivityTechnique): AppView {
  return technique === 'POMODORO' ? 'technique-pomodoro-break' : 'technique-5217-break'
}

function summaryViewFor(technique: ProductivityTechnique): AppView {
  return technique === 'POMODORO' ? 'technique-pomodoro-summary' : 'technique-5217-summary'
}

function timerConfiguration(timer = techniqueTimer.value) {
  return {
    work_minutes: timer.workMinutes,
    break_minutes: timer.breakMinutes,
    cycles: timer.targetCycles,
    effective_seconds: timer.effectiveSeconds,
    break_seconds: timer.breakSeconds,
  }
}

function configNumber(
  configuration: Record<string, unknown>,
  key: string,
  fallback: number,
  allowZero = false,
) {
  const value = configuration[key]
  if (typeof value !== 'number' || !Number.isFinite(value)) return fallback
  if (allowZero ? value < 0 : value <= 0) return fallback
  return value
}

function timeBlocksFromConfiguration(configuration: Record<string, unknown>) {
  const blocks = configuration.blocks
  if (!Array.isArray(blocks)) return defaultTimeBlocks()

  const parsedBlocks = blocks
    .map((block, index): TimeBlock | null => {
      if (!block || typeof block !== 'object') return null
      const item = block as Partial<TimeBlock>
      if (typeof item.title !== 'string' || typeof item.start !== 'string' || typeof item.end !== 'string') {
        return null
      }
      return {
        id: typeof item.id === 'number' ? item.id : Date.now() + index,
        title: item.title,
        start: item.start,
        end: item.end,
        category: typeof item.category === 'string' ? item.category : 'Estudio',
      }
    })
    .filter((block): block is TimeBlock => block !== null)

  return parsedBlocks.sort((a, b) => a.start.localeCompare(b.start))
}

function timerFromProductivitySession(session: ProductivitySession): TechniqueTimerState {
  const defaultTimer = emptyTechniqueTimer(session.technique)
  const configuration = session.configuration || {}
  const workMinutes = configNumber(configuration, 'work_minutes', defaultTimer.workMinutes)
  const breakMinutes = configNumber(configuration, 'break_minutes', defaultTimer.breakMinutes)
  const targetCycles = configNumber(configuration, 'cycles', defaultTimer.targetCycles)
  const focusDurationSeconds = workMinutes * 60
  const breakDurationSeconds = breakMinutes * 60
  const cycleDurationSeconds = focusDurationSeconds + breakDurationSeconds
  const elapsedSeconds = Math.max(
    Math.floor((Date.now() - new Date(session.start_at).getTime()) / 1000),
    0,
  )
  const maxSessionSeconds = cycleDurationSeconds * targetCycles

  if (elapsedSeconds >= maxSessionSeconds) {
    return {
      ...defaultTimer,
      phase: 'summary',
      workMinutes,
      breakMinutes,
      targetCycles,
      currentCycle: targetCycles,
      completedCycles: targetCycles,
      remainingSeconds: 0,
      effectiveSeconds: targetCycles * focusDurationSeconds,
      breakSeconds: targetCycles * breakDurationSeconds,
      isRunning: false,
    }
  }

  const completedFullCycles = Math.floor(elapsedSeconds / cycleDurationSeconds)
  const secondsInsideCycle = elapsedSeconds % cycleDurationSeconds

  if (secondsInsideCycle < focusDurationSeconds) {
    return {
      ...defaultTimer,
      phase: 'focus',
      workMinutes,
      breakMinutes,
      targetCycles,
      currentCycle: completedFullCycles + 1,
      completedCycles: completedFullCycles,
      remainingSeconds: focusDurationSeconds - secondsInsideCycle,
      effectiveSeconds: completedFullCycles * focusDurationSeconds + secondsInsideCycle,
      breakSeconds: completedFullCycles * breakDurationSeconds,
      isRunning: true,
    }
  }

  const breakElapsedSeconds = secondsInsideCycle - focusDurationSeconds
  return {
    ...defaultTimer,
    phase: 'break',
    workMinutes,
    breakMinutes,
    targetCycles,
    currentCycle: completedFullCycles + 1,
    completedCycles: completedFullCycles + 1,
    remainingSeconds: breakDurationSeconds - breakElapsedSeconds,
    effectiveSeconds: (completedFullCycles + 1) * focusDurationSeconds,
    breakSeconds: completedFullCycles * breakDurationSeconds + breakElapsedSeconds,
    isRunning: true,
  }
}

async function createProductivitySession(technique: ProductivityTechnique, configuration: Record<string, unknown>) {
  return apiRequest<ProductivitySession>('/productivity-sessions/', {
    method: 'POST',
    body: JSON.stringify({
      technique,
      status: 'IN_PROGRESS',
      configuration,
    }),
  })
}

function startTechniqueInterval() {
  clearTechniqueInterval()
  techniqueInterval = window.setInterval(tickTechniqueTimer, 1000)
}

function tickTechniqueTimer() {
  const timer = techniqueTimer.value
  if (!timer.isRunning) return

  const isFocus = timer.phase === 'focus'
  if (timer.remainingSeconds <= 1) {
    techniqueTimer.value = {
      ...timer,
      remainingSeconds: 0,
      effectiveSeconds: timer.effectiveSeconds + (isFocus ? 1 : 0),
      breakSeconds: timer.breakSeconds + (isFocus ? 0 : 1),
    }
    completeTechniquePhase()
    return
  }

  techniqueTimer.value = {
    ...timer,
    remainingSeconds: timer.remainingSeconds - 1,
    effectiveSeconds: timer.effectiveSeconds + (isFocus ? 1 : 0),
    breakSeconds: timer.breakSeconds + (isFocus ? 0 : 1),
  }
}

function completeTechniquePhase() {
  const timer = techniqueTimer.value
  if (timer.phase === 'focus') {
    const completedCycles = Math.min(timer.completedCycles + 1, timer.targetCycles)
    techniqueTimer.value = {
      ...timer,
      phase: 'break',
      completedCycles,
      remainingSeconds: timer.breakMinutes * 60,
      isRunning: true,
    }
    setCurrentView(breakViewFor(timer.technique), { remember: false })
    return
  }

  if (timer.completedCycles >= timer.targetCycles) {
    showTechniqueSummary()
    return
  }

  techniqueTimer.value = {
    ...timer,
    phase: 'focus',
    currentCycle: timer.completedCycles + 1,
    remainingSeconds: timer.workMinutes * 60,
    isRunning: true,
  }
  setCurrentView(focusViewFor(timer.technique), { remember: false })
}

function pauseTechniqueTimer() {
  techniqueTimer.value = { ...techniqueTimer.value, isRunning: false }
}

function resumeTechniqueTimer() {
  techniqueTimer.value = { ...techniqueTimer.value, isRunning: true }
  startTechniqueInterval()
}

function showTechniqueSummary() {
  clearTechniqueInterval()
  techniqueTimer.value = { ...techniqueTimer.value, phase: 'summary', isRunning: false }
  setCurrentView(summaryViewFor(techniqueTimer.value.technique), { remember: false })
}

async function finishTechniqueSession(statusValue: 'COMPLETED' | 'INTERRUPTED', navigateAfter = true) {
  const session = activeProductivitySession.value
  if (!session) {
    if (navigateAfter) openTechniques()
    return
  }

  techniqueSaving.value = true
  try {
    const timer = techniqueTimer.value
    const totalSeconds = timer.effectiveSeconds + timer.breakSeconds
    const updated = await apiRequest<ProductivitySession>(`/productivity-sessions/${session.id}/finish/`, {
      method: 'POST',
      body: JSON.stringify({
        status: statusValue,
        total_duration: Math.ceil(totalSeconds / 60),
        effective_time: Math.ceil(timer.effectiveSeconds / 60),
        completed_cycles: timer.completedCycles,
        configuration: timerConfiguration(timer),
      }),
    })
    productivitySessions.value = [
      updated,
      ...productivitySessions.value.filter((item) => item.id !== updated.id),
    ]
    activeProductivitySession.value = null
    await loadDashboard()
    if (navigateAfter) openTechniques()
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudo guardar la sesión.'
  } finally {
    techniqueSaving.value = false
  }
}

function cancelTechniqueSession() {
  clearTechniqueInterval()
  void finishTechniqueSession('INTERRUPTED')
}

function finishTechniqueStudy() {
  void finishTechniqueSession('COMPLETED')
}

async function restartTechniqueStudy() {
  const technique = techniqueTimer.value.technique
  await finishTechniqueSession('COMPLETED', false)
  await startTechnique(technique)
}

function openTechniques() {
  resetTechniqueState()
  setCurrentView('techniques')
  void loadProductivitySessions()
}

async function startTechnique(technique: ProductivityTechnique) {
  techniqueMessage.value = ''
  if (technique === 'TIME_BLOCKING') {
    await startTimeBlocking()
    return
  }

  const timer = emptyTechniqueTimer(technique)
  techniqueTimer.value = timer
  techniqueLoading.value = true
  try {
    activeProductivitySession.value = await createProductivitySession(technique, timerConfiguration(timer))
    techniqueTimer.value = { ...timer, isRunning: true }
    setCurrentView(focusViewFor(technique))
    startTechniqueInterval()
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudo iniciar la técnica.'
  } finally {
    techniqueLoading.value = false
  }
}

function resumeProductivitySession(session: ProductivitySession) {
  if (session.status !== 'IN_PROGRESS') return
  clearTechniqueInterval()
  techniqueMessage.value = ''
  activeProductivitySession.value = session

  if (session.technique === 'TIME_BLOCKING') {
    timeBlocks.value = timeBlocksFromConfiguration(session.configuration || {})
    setCurrentView('technique-time-blocking')
    return
  }

  const timer = timerFromProductivitySession(session)
  techniqueTimer.value = timer

  if (timer.phase === 'summary') {
    setCurrentView(summaryViewFor(timer.technique))
    return
  }

  setCurrentView(timer.phase === 'break' ? breakViewFor(timer.technique) : focusViewFor(timer.technique))
  if (timer.isRunning) startTechniqueInterval()
}

function parseTimeToMinutes(value: string) {
  const [hourValue = '0', minuteValue = '0'] = value.split(':')
  const hour = Number(hourValue)
  const minute = Number(minuteValue)
  if (!Number.isFinite(hour) || !Number.isFinite(minute)) return 0
  return hour * 60 + minute
}

function minutesBetween(start: string, end: string) {
  return Math.max(parseTimeToMinutes(end) - parseTimeToMinutes(start), 0)
}

function addMinutesToTime(value: string, minutes: number) {
  const total = parseTimeToMinutes(value) + minutes
  const nextHour = Math.floor(total / 60) % 24
  const nextMinute = total % 60
  return `${String(nextHour).padStart(2, '0')}:${String(nextMinute).padStart(2, '0')}`
}

async function startTimeBlocking() {
  techniqueLoading.value = true
  techniqueMessage.value = ''
  timeBlocks.value = defaultTimeBlocks()
  try {
    activeProductivitySession.value = await createProductivitySession('TIME_BLOCKING', {
      block_minutes: 60,
      blocks: timeBlocks.value,
    })
    setCurrentView('technique-time-blocking')
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudo iniciar time blocking.'
  } finally {
    techniqueLoading.value = false
  }
}

async function saveTimeBlockingDraft() {
  const session = activeProductivitySession.value
  if (!session || session.technique !== 'TIME_BLOCKING' || session.status !== 'IN_PROGRESS') return

  try {
    const updated = await apiRequest<ProductivitySession>(`/productivity-sessions/${session.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        configuration: {
          block_minutes: 60,
          blocks: timeBlocks.value,
        },
      }),
    })
    activeProductivitySession.value = updated
    productivitySessions.value = [
      updated,
      ...productivitySessions.value.filter((item) => item.id !== updated.id),
    ]
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudo guardar el bloque.'
  }
}

function addTimeBlock(block: Omit<TimeBlock, 'id'>) {
  timeBlocks.value = [
    ...timeBlocks.value,
    {
      ...block,
      id: Date.now(),
    },
  ].sort((a, b) => a.start.localeCompare(b.start))
  void saveTimeBlockingDraft()
}

function removeTimeBlock(blockId: number) {
  timeBlocks.value = timeBlocks.value.filter((block) => block.id !== blockId)
  void saveTimeBlockingDraft()
}

async function finishTimeBlocking() {
  const session = activeProductivitySession.value
  if (!session) {
    openTechniques()
    return
  }

  if (!timeBlocks.value.length) {
    techniqueMessage.value = 'Añade al menos un bloque antes de finalizar el estudio.'
    return
  }

  const effectiveMinutes = timeBlocks.value.reduce(
    (total, block) => total + minutesBetween(block.start, block.end),
    0,
  )
  techniqueSaving.value = true
  try {
    const updated = await apiRequest<ProductivitySession>(`/productivity-sessions/${session.id}/finish/`, {
      method: 'POST',
      body: JSON.stringify({
        status: 'COMPLETED',
        total_duration: effectiveMinutes,
        effective_time: effectiveMinutes,
        completed_cycles: timeBlocks.value.length,
        configuration: {
          block_minutes: 60,
          blocks: timeBlocks.value,
        },
      }),
    })
    productivitySessions.value = [
      updated,
      ...productivitySessions.value.filter((item) => item.id !== updated.id),
    ]
    activeProductivitySession.value = null
    await loadDashboard()
    openTechniques()
  } catch (error) {
    techniqueMessage.value = error instanceof Error ? error.message : 'No se pudo guardar time blocking.'
  } finally {
    techniqueSaving.value = false
  }
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

async function createInitialTaskCollaboration(task: Task) {
  const userIdentifier = taskForm.value.collaboratorIdentifier.trim()
  if (!userIdentifier) return null

  return apiRequest<Collaboration>('/collaborations/', {
    method: 'POST',
    body: JSON.stringify({
      user: userIdForIdentifier(userIdentifier),
      user_identifier: userIdentifier,
      resource_type: 'TASK',
      task: task.id,
      role: taskForm.value.collaboratorRole,
    }),
  })
}

async function createInitialProjectCollaboration(project: Project) {
  const userIdentifier = projectForm.value.collaboratorIdentifier.trim()
  if (!userIdentifier) return null

  return apiRequest<Collaboration>('/collaborations/', {
    method: 'POST',
    body: JSON.stringify({
      user: userIdForIdentifier(userIdentifier),
      user_identifier: userIdentifier,
      resource_type: 'PROJECT',
      project: project.id,
      role: projectForm.value.collaboratorRole,
    }),
  })
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
    try {
      const collaboration = await createInitialTaskCollaboration(createdTask)
      if (collaboration) {
        collaborations.value = [
          collaboration,
          ...collaborations.value.filter((item) => item.id !== collaboration.id),
        ]
      }
    } catch (error) {
      selectedTaskId.value = createdTask.id
      taskShareMessage.value =
        error instanceof Error ? `Tarea creada. ${error.message}` : 'Tarea creada. No se pudo invitar al colaborador.'
      resetTaskForm()
      setCurrentView('task-detail', { remember: false })
      return
    }
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
    try {
      const collaboration = await createInitialProjectCollaboration(createdProject)
      if (collaboration) {
        collaborations.value = [
          collaboration,
          ...collaborations.value.filter((item) => item.id !== collaboration.id),
        ]
      }
    } catch (error) {
      selectedProjectId.value = createdProject.id
      projectShareMessage.value =
        error instanceof Error ? `Proyecto creado. ${error.message}` : 'Proyecto creado. No se pudo invitar al colaborador.'
      resetProjectForm()
      setCurrentView('project-detail', { remember: false })
      return
    }
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

function userIdForIdentifier(identifier: string) {
  const normalizedIdentifier = identifier.trim().toLowerCase()
  const user = users.value.find(
    (item) =>
      item.username.toLowerCase() === normalizedIdentifier ||
      item.email.toLowerCase() === normalizedIdentifier,
  )
  return user?.id
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
        user: userIdForIdentifier(userIdentifier),
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

async function respondToCollaboration(collaboration: Collaboration, action: 'accept' | 'reject') {
  collaborationLoading.value = true
  dashboardMessage.value = ''
  try {
    const updated = await apiRequest<Collaboration>(`/collaborations/${collaboration.id}/${action}/`, {
      method: 'POST',
    })
    collaborations.value = collaborations.value.map((item) => (item.id === updated.id ? updated : item))
    await loadDashboard()
  } catch (error) {
    dashboardMessage.value = error instanceof Error ? error.message : 'No se pudo responder a la invitacion.'
  } finally {
    collaborationLoading.value = false
  }
}

function acceptCollaboration(collaboration: Collaboration) {
  void respondToCollaboration(collaboration, 'accept')
}

function rejectCollaboration(collaboration: Collaboration) {
  void respondToCollaboration(collaboration, 'reject')
}

async function removeCollaboration(collaboration: Collaboration) {
  const isProjectCollaboration = collaboration.resource_type === 'PROJECT'
  if (isProjectCollaboration) {
    projectShareMessage.value = ''
  } else {
    taskShareMessage.value = ''
  }

  shareLoading.value = true
  try {
    await apiRequest<null>(`/collaborations/${collaboration.id}/`, { method: 'DELETE' })
    collaborations.value = collaborations.value.filter((item) => item.id !== collaboration.id)
    if (isProjectCollaboration) {
      projectShareMessage.value = 'Colaborador eliminado correctamente.'
    } else {
      taskShareMessage.value = 'Colaborador eliminado correctamente.'
    }
    await loadDashboard()
  } catch (error) {
    const message = error instanceof Error ? error.message : 'No se pudo eliminar el colaborador.'
    if (isProjectCollaboration) {
      projectShareMessage.value = message
    } else {
      taskShareMessage.value = message
    }
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
        user: userIdForIdentifier(userIdentifier),
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

async function deleteAccount() {
  deleteAccountMessage.value = ''
  const password = deleteAccountForm.value.password
  if (!password) {
    deleteAccountMessage.value = 'Introduce tu contrasena para confirmar la eliminacion.'
    return
  }

  accountDeleting.value = true
  try {
    await apiRequest('/auth/delete-account/', {
      method: 'DELETE',
      body: JSON.stringify({ password }),
    })
    clearSessionState()
  } catch (error) {
    deleteAccountMessage.value = error instanceof Error ? error.message : 'No se pudo eliminar la cuenta.'
  } finally {
    accountDeleting.value = false
  }
}

function clearSessionState() {
  clearTokens()
  profile.value = null
  tasks.value = []
  projects.value = []
  dashboard.value = null
  calendar.value = null
  achievements.value = []
  collaborations.value = []
  notifications.value = []
  users.value = []
  productivitySessions.value = []
  selectedTaskId.value = null
  selectedProjectId.value = null
  resetEditProfileForm()
  resetDeleteAccountForm()
  resetTaskForm()
  resetProjectForm()
  resetTaskShareForm()
  resetProjectShareForm()
  clearAuthForms()
  authMode.value = 'login'
  setCurrentView('auth', { clearHistory: true })
  authMessage.value = ''
  dashboardMessage.value = ''
  editProfileMessage.value = ''
  deleteAccountMessage.value = ''
  taskMessage.value = ''
  projectMessage.value = ''
  taskShareMessage.value = ''
  projectShareMessage.value = ''
  calendarMessage.value = ''
  exportMessage.value = ''
  achievementMessage.value = ''
  resetExportForm()
  resetTechniqueState()
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

onBeforeUnmount(() => {
  clearTechniqueInterval()
})

watch(
  () => route.fullPath,
  () => {
    if (syncingRouterRoute.value) return
    void applyRouteToState()
  },
)

onMounted(() => {
  void applyRouteToState()
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

    <PantallaRecuperarContrasena
      v-else-if="currentView === 'auth' && authMode === 'password-reset'"
      :form="passwordResetForm"
      :loading="loading"
      :message="authMessage"
      @request-reset="submitPasswordResetRequest"
      @confirm-reset="submitPasswordResetConfirm"
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
      :productivity-sessions="productivitySessions"
      :achievements="achievements"
      :dashboard-loading="dashboardLoading"
      :dashboard-message="dashboardMessage"
      :pending-collaborations="pendingCollaborations"
      :collaboration-loading="collaborationLoading"
      :notifications="notifications"
      :notification-loading="notificationLoading"
      @open-profile="openProfile"
      @navigate="handleNavigation"
      @accept-collaboration="acceptCollaboration"
      @reject-collaboration="rejectCollaboration"
      @mark-notification-read="markNotificationRead"
    />

    <PantallaCalendario
      v-else-if="currentView === 'calendar'"
      :calendar="calendar"
      :tasks="tasks"
      :selected-date="calendarDate"
      :initials="initials"
      :loading="calendarLoading"
      :message="calendarMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @change-month="changeCalendarMonth"
      @open-item="openCalendarItem"
    />

    <PantallaEstadisticas
      v-else-if="currentView === 'statistics'"
      :initials="initials"
      :tasks="tasks"
      :projects="projects"
      :sessions="productivitySessions"
      :dashboard="dashboard"
      :period="statisticsPeriod"
      :selected-date="statisticsDate"
      :loading="dashboardLoading"
      :message="dashboardMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @change-period="changeStatisticsPeriod"
    />

    <PantallaLogros
      v-else-if="currentView === 'achievements'"
      :initials="initials"
      :achievements="achievements"
      :loading="achievementLoading"
      :message="achievementMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
    />

    <PantallaExportarDatos
      v-else-if="currentView === 'export'"
      :form="exportForm"
      :projects="projects"
      :initials="initials"
      :loading="exportLoading"
      :message="exportMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @submit="submitExport"
    />

    <PantallaTecnicas
      v-else-if="currentView === 'techniques'"
      :initials="initials"
      :loading="techniqueLoading"
      :message="techniqueMessage"
      :sessions="productivitySessions"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @start-technique="startTechnique"
      @resume-session="resumeProductivitySession"
    />

    <PantallaPomodoro
      v-else-if="currentView === 'technique-pomodoro'"
      :timer="techniqueTimer"
      :initials="initials"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @pause="pauseTechniqueTimer"
      @resume="resumeTechniqueTimer"
      @cancel="cancelTechniqueSession"
      @finish="showTechniqueSummary"
    />

    <PantallaPomodoroDescanso
      v-else-if="currentView === 'technique-pomodoro-break'"
      :timer="techniqueTimer"
      :initials="initials"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @pause="pauseTechniqueTimer"
      @resume="resumeTechniqueTimer"
      @finish-break="completeTechniquePhase"
    />

    <PantallaResumenPomodoro
      v-else-if="currentView === 'technique-pomodoro-summary'"
      :timer="techniqueTimer"
      :initials="initials"
      :saving="techniqueSaving"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @finish="finishTechniqueStudy"
      @restart="restartTechniqueStudy"
    />

    <Pantalla5217
      v-else-if="currentView === 'technique-5217'"
      :timer="techniqueTimer"
      :initials="initials"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @pause="pauseTechniqueTimer"
      @resume="resumeTechniqueTimer"
      @cancel="cancelTechniqueSession"
      @finish="showTechniqueSummary"
    />

    <Pantalla5217Descanso
      v-else-if="currentView === 'technique-5217-break'"
      :timer="techniqueTimer"
      :initials="initials"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @pause="pauseTechniqueTimer"
      @resume="resumeTechniqueTimer"
      @finish-break="completeTechniquePhase"
    />

    <PantallaResumen5217
      v-else-if="currentView === 'technique-5217-summary'"
      :timer="techniqueTimer"
      :initials="initials"
      :saving="techniqueSaving"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @finish="finishTechniqueStudy"
      @restart="restartTechniqueStudy"
    />

    <PantallaTimeBlocking
      v-else-if="currentView === 'technique-time-blocking'"
      :blocks="timeBlocks"
      :initials="initials"
      :saving="techniqueSaving"
      :message="techniqueMessage"
      @navigate="handleNavigation"
      @open-profile="openProfile"
      @add-block="addTimeBlock"
      @remove-block="removeTimeBlock"
      @finish="finishTimeBlocking"
    />

    <PantallaMisTareas
      v-else-if="currentView === 'tasks'"
      :tasks="tasks"
      :projects="projects"
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
      @remove-collaboration="removeCollaboration"
    />

    <PantallaCrearTarea
      v-else-if="currentView === 'task-create'"
      :form="taskForm"
      :projects="projects"
      :users="users"
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
      :task="selectedTask"
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
      :projects="projects"
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
      @remove-collaboration="removeCollaboration"
    />

    <PantallaCrearProyecto
      v-else-if="currentView === 'project-create'"
      :form="projectForm"
      :users="users"
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
      :project="selectedProject"
      :tasks="selectedProjectTasks"
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
      :delete-form="deleteAccountForm"
      :delete-loading="accountDeleting"
      :delete-message="deleteAccountMessage"
      @go-home="openDashboard"
      @navigate="handleNavigation"
      @edit-profile="openEditProfile"
      @delete-account="deleteAccount"
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
.app-shell.has-back-button :global(.task-edit-content),
.app-shell.has-back-button :global(.delete-content),
.app-shell.has-back-button :global(.projects-content),
.app-shell.has-back-button :global(.project-content),
.app-shell.has-back-button :global(.project-form-content),
.app-shell.has-back-button :global(.project-edit-content),
.app-shell.has-back-button :global(.calendar-content),
.app-shell.has-back-button :global(.achievements-content),
.app-shell.has-back-button :global(.export-content),
.app-shell.has-back-button :global(.techniques-content),
.app-shell.has-back-button :global(.timer-content),
.app-shell.has-back-button :global(.break-content),
.app-shell.has-back-button :global(.summary-content),
.app-shell.has-back-button :global(.blocking-content) {
  padding-top: 112px;
}

.app-shell.has-back-button :global(.tasks-content),
.app-shell.has-back-button :global(.task-content),
.app-shell.has-back-button :global(.task-form-content),
.app-shell.has-back-button :global(.task-edit-content),
.app-shell.has-back-button :global(.delete-content),
.app-shell.has-back-button :global(.projects-content),
.app-shell.has-back-button :global(.project-content),
.app-shell.has-back-button :global(.project-form-content),
.app-shell.has-back-button :global(.project-edit-content),
.app-shell.has-back-button :global(.calendar-content) {
  padding-top: 136px;
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
