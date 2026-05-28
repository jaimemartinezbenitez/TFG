<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PantallaInicio from './PantallaInicio.vue'
import PantallaIniciarSesion from './PantallaIniciarSesion.vue'
import PantallaRegistro from './PantallaRegistro.vue'
import type {
  ActivityItem,
  AuthMode,
  DashboardData,
  DashboardTaskItem,
  LoginForm,
  Project,
  RegisterForm,
  Task,
  UserProfile,
} from './types'

const API_BASE = '/api'

const currentView = ref<'auth' | 'dashboard'>('auth')
const authMode = ref<AuthMode>('register')
const loading = ref(false)
const dashboardLoading = ref(false)
const authMessage = ref('')
const dashboardMessage = ref('')
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

const profile = ref<UserProfile | null>(null)
const tasks = ref<Task[]>([])
const projects = ref<Project[]>([])
const dashboard = ref<DashboardData | null>(null)

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

const displayName = computed(() => {
  const username = profile.value?.first_name || profile.value?.username || registerForm.value.username
  if (!username) return 'Jaime'
  return username.charAt(0).toUpperCase() + username.slice(1)
})

const initials = computed(() => displayName.value.slice(0, 1).toUpperCase())

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
      isPending: task.status !== 'COMPLETED',
    })),
)

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
  const tokenResponse = await apiRequest<{ access: string; refresh: string }>('/auth/token/', {
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
    currentView.value = 'dashboard'
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
    currentView.value = 'dashboard'
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
    const [profileData, taskData, projectData, dashboardData] = await Promise.all([
      apiRequest<UserProfile>('/auth/profile/'),
      apiRequest<Task[]>('/tasks/'),
      apiRequest<Project[]>('/projects/'),
      apiRequest<DashboardData>('/statistics/dashboard/'),
    ])
    profile.value = profileData
    tasks.value = taskData
    projects.value = projectData
    dashboard.value = dashboardData
  } catch (error) {
    dashboardMessage.value = error instanceof Error ? error.message : 'No se pudo cargar el inicio.'
    clearTokens()
    currentView.value = 'auth'
  } finally {
    dashboardLoading.value = false
  }
}

function switchAuthMode(mode: AuthMode) {
  clearAuthForms()
  authMode.value = mode
  authMessage.value = ''
}

function logout() {
  clearTokens()
  profile.value = null
  tasks.value = []
  projects.value = []
  dashboard.value = null
  clearAuthForms()
  currentView.value = 'auth'
  authMode.value = 'login'
  authMessage.value = ''
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
    IN_PROGRESS: 'EN CURSO',
    COMPLETED: 'COMPLETADO',
    CANCELLED: 'CANCELADA',
  }
  return labels[status]
}

onMounted(() => {
  if (accessToken.value) {
    currentView.value = 'dashboard'
    void loadDashboard()
  }
})
</script>

<template>
  <main class="app-shell">
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
      v-else
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
      @logout="logout"
    />
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
:global(input) {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
}
</style>
