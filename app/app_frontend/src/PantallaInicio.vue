<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type {
  Achievement,
  ActivityItem,
  Collaboration,
  DashboardTaskItem,
  ProductivitySession,
  ProductivityTechnique,
} from './types'

const props = defineProps<{
  displayName: string
  initials: string
  pendingTasks: number
  completedTasks: number
  activeProjects: number
  effectiveMinutes: number
  upcomingTasks: DashboardTaskItem[]
  recentActivity: ActivityItem[]
  productivitySessions: ProductivitySession[]
  achievements: Achievement[]
  dashboardLoading: boolean
  dashboardMessage: string
  pendingCollaborations: Collaboration[]
  collaborationLoading: boolean
}>()

const emit = defineEmits<{
  'open-profile': []
  navigate: [section: string]
  'accept-collaboration': [collaboration: Collaboration]
  'reject-collaboration': [collaboration: Collaboration]
}>()

const orderedProductivitySessions = computed(() =>
  [...props.productivitySessions].sort(
    (a, b) => new Date(b.start_at).getTime() - new Date(a.start_at).getTime(),
  ),
)

const completedProductivitySessions = computed(() =>
  props.productivitySessions.filter((session) => session.status === 'COMPLETED'),
)

const totalFocusMinutes = computed(() =>
  completedProductivitySessions.value.reduce((total, session) => total + session.effective_time, 0),
)

const completedCycles = computed(() =>
  completedProductivitySessions.value.reduce((total, session) => total + session.completed_cycles, 0),
)

const recentProductivitySessions = computed(() => orderedProductivitySessions.value.slice(0, 3))

const recentAchievements = computed(() =>
  [...props.achievements]
    .sort((a, b) => new Date(b.achieved_at).getTime() - new Date(a.achieved_at).getTime())
    .slice(0, 4),
)

const favoriteTechnique = computed(() => {
  const counts = completedProductivitySessions.value.reduce<Record<ProductivityTechnique, number>>(
    (accumulator, session) => {
      accumulator[session.technique] += 1
      return accumulator
    },
    { POMODORO: 0, TIME_BLOCKING: 0, FIFTY_TWO_SEVENTEEN: 0 },
  )
  const [technique, total] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0] as [
    ProductivityTechnique,
    number,
  ]
  return total > 0 ? techniqueLabel(technique) : 'Sin datos'
})

function achievementSymbol(name: string) {
  const symbols: Record<string, string> = {
    'Primeros pasos': '★',
    'Enfoque total': '◴',
    Constante: '♛',
    Productivo: '↗',
    Madrugador: '☼',
    Maratonista: '◆',
    Imparable: '∞',
    Experto: '✦',
    'Semana en marcha': 'Ⅰ',
    'Sprint semanal': 'Ⅴ',
    'Semana enfocada': '⌁',
    'Ritmo semanal': '▣',
    'Mes activo': '◇',
    'Mes productivo': '◈',
    'Mes de enfoque': '◉',
    'Constancia mensual': '▰',
    'Ano constante': '✧',
    'Ano productivo': '⬡',
    'Ano de enfoque': '✺',
    'Maestria anual': '♢',
  }
  return symbols[name] || '✓'
}

function achievementTone(name: string) {
  if (name.includes('Semana')) return 'achievement-weekly'
  if (name.includes('Mes') || name.includes('mensual')) return 'achievement-monthly'
  if (name.includes('Ano') || name.includes('anual')) return 'achievement-yearly'
  return 'achievement-general'
}

function achievementDate(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
  }).format(new Date(value))
}

function invitationType(collaboration: Collaboration) {
  return collaboration.resource_type === 'TASK' ? 'Tarea' : 'Proyecto'
}

function techniqueLabel(technique: ProductivityTechnique) {
  const labels = {
    POMODORO: 'Pomodoro',
    TIME_BLOCKING: 'Time blocking',
    FIFTY_TWO_SEVENTEEN: '52/17',
  }
  return labels[technique]
}

function sessionStatusLabel(status: ProductivitySession['status']) {
  const labels = {
    IN_PROGRESS: 'En curso',
    COMPLETED: 'Completada',
    INTERRUPTED: 'Interrumpida',
  }
  return labels[status]
}

function durationLabel(minutes: number) {
  if (!minutes) return '0m'
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (!hours) return `${remainingMinutes}m`
  if (!remainingMinutes) return `${hours}h`
  return `${hours}h ${remainingMinutes}m`
}

function dateLabel(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}
</script>

<template>
  <section class="dashboard-frame">
    <MenuLateral active="inicio" @navigate="emit('navigate', $event)" />

    <section class="dashboard-content">
      <header class="dashboard-header">
        <div>
          <h1>¡Hola, {{ props.displayName }}!</h1>
          <p>Aqui tienes un resumen de tu productividad</p>
        </div>
        <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
          <span>{{ props.initials }}</span>
        </button>
      </header>

      <p v-if="props.dashboardMessage" class="dashboard-error">{{ props.dashboardMessage }}</p>
      <p v-else-if="props.dashboardLoading" class="loading-copy">Cargando resumen...</p>

      <div class="stats-row" aria-label="Resumen de productividad">
        <article>
          <span>Tareas pendientes</span>
          <strong class="danger">{{ props.pendingTasks }}</strong>
        </article>
        <article>
          <span>Tareas completadas</span>
          <strong class="accent">{{ props.completedTasks }}</strong>
        </article>
        <article>
          <span>Proyectos activos</span>
          <strong>{{ props.activeProjects }}</strong>
        </article>
        <article>
          <span>Minutos efectivos</span>
          <strong>{{ props.effectiveMinutes }}</strong>
        </article>
      </div>

      <section v-if="props.pendingCollaborations.length" class="invitations-panel" aria-label="Invitaciones de colaboracion pendientes">
        <h2>Invitaciones pendientes:</h2>
        <ul>
          <li v-for="collaboration in props.pendingCollaborations" :key="collaboration.id">
            <div>
              <strong>{{ invitationType(collaboration) }}: {{ collaboration.resource_name }}</strong>
              <span>{{ collaboration.owner?.username }} te invita como {{ collaboration.role }}</span>
            </div>
            <div class="invitation-actions">
              <button type="button" :disabled="props.collaborationLoading" @click="emit('accept-collaboration', collaboration)">Aceptar</button>
              <button class="reject-button" type="button" :disabled="props.collaborationLoading" @click="emit('reject-collaboration', collaboration)">Rechazar</button>
            </div>
          </li>
        </ul>
      </section>

      <div class="dashboard-grid">
        <section class="panel">
          <h2>Tareas proximas:</h2>
          <ul class="task-list">
            <li v-for="task in props.upcomingTasks" :key="task.id">
              <span class="alert-icon">!</span>
              <span class="task-title">{{ task.title }}</span>
              <time>{{ task.dateLabel }}</time>
            </li>
            <li v-if="!props.upcomingTasks.length" class="empty-row">No hay tareas proximas.</li>
          </ul>
        </section>

        <section class="panel">
          <h2>Actividad reciente:</h2>
          <ul class="activity-list">
            <li v-for="task in props.recentActivity" :key="task.id">
              <span class="activity-dot" :class="task.statusClass"></span>
              <span class="task-title">{{ task.title }}</span>
              <small>{{ task.statusLabel }}</small>
            </li>
            <li v-if="!props.recentActivity.length" class="empty-row">Aun no hay actividad.</li>
          </ul>
        </section>
      </div>


      <div class="dashboard-lower-grid">
        <section class="achievements-panel" aria-label="Logros obtenidos">
        <div class="section-heading">
          <h2>Logros obtenidos:</h2>
          <button type="button" @click="emit('navigate', 'logros')">Ver todos</button>
        </div>

        <ul>
          <li v-for="achievement in recentAchievements" :key="achievement.id">
            <span class="achievement-badge" :class="achievementTone(achievement.name)">
              {{ achievementSymbol(achievement.name) }}
            </span>
            <div>
              <strong>{{ achievement.name }}</strong>
              <small>{{ achievement.description }}</small>
            </div>
            <time>{{ achievementDate(achievement.achieved_at) }}</time>
          </li>
          <li v-if="!recentAchievements.length" class="empty-row">Aun no hay logros desbloqueados.</li>
        </ul>
        </section>

        <section class="sessions-panel" aria-label="Resumen de sesiones de productividad">
        <div class="sessions-summary">
          <article>
            <strong>{{ completedProductivitySessions.length }}</strong>
            <span>sesiones completadas</span>
          </article>
          <article>
            <strong>{{ durationLabel(totalFocusMinutes) }}</strong>
            <span>tiempo de enfoque</span>
          </article>
          <article>
            <strong>{{ completedCycles }}</strong>
            <span>ciclos completados</span>
          </article>
          <article>
            <strong>{{ favoriteTechnique }}</strong>
            <span>técnica más usada</span>
          </article>
        </div>

        <div class="sessions-recent">
          <h2>Sesiones de productividad:</h2>
          <ul>
            <li v-for="session in recentProductivitySessions" :key="session.id">
              <span class="session-dot" :class="`session-${session.status.toLowerCase()}`"></span>
              <strong>{{ techniqueLabel(session.technique) }}</strong>
              <small>{{ sessionStatusLabel(session.status) }}</small>
              <time>{{ durationLabel(session.effective_time) }} · {{ dateLabel(session.start_at) }}</time>
            </li>
            <li v-if="!recentProductivitySessions.length" class="empty-row">
              Aun no hay sesiones de productividad registradas.
            </li>
          </ul>
        </div>
        </section>
      </div>
    </section>
  </section>
</template>

<style scoped>
.dashboard-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.dashboard-content {
  min-width: 0;
  padding: 54px 74px 54px 60px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
}

.dashboard-header h1 {
  margin: 0;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.dashboard-header p {
  margin: 16px 0 0;
  font-size: 1.22rem;
}

.avatar-button {
  width: 62px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 5px solid #715cff;
  border-radius: 50%;
  color: #fff;
  background:
    linear-gradient(#8794ea 0 0) center 14px / 24px 24px no-repeat,
    linear-gradient(#8794ea 0 0) center 39px / 42px 18px no-repeat,
    #f8f8ff;
  cursor: pointer;
}

.avatar-button span {
  position: relative;
  top: -5px;
  font-weight: 800;
}

.stats-row {
  max-width: 860px;
  margin-top: 26px;
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 28px;
  text-align: center;
}

.stats-row article {
  display: grid;
  gap: 12px;
}

.stats-row span {
  font-size: 1rem;
}

.stats-row strong {
  font-size: 2rem;
  font-weight: 500;
}

.stats-row .danger {
  color: #ff2d3b;
  font-weight: 800;
}

.stats-row .accent {
  color: #3f6df6;
  font-weight: 800;
}


.dashboard-lower-grid {
  width: min(100%, 1220px);
  display: grid;
  grid-template-columns: minmax(430px, 0.95fr) minmax(460px, 1fr);
  gap: 42px;
  align-items: start;
  margin-top: 30px;
}

.achievements-panel,
.sessions-panel {
  min-width: 0;
}

.achievements-panel {
  width: 100%;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 12px;
}

.section-heading h2 {
  margin: 0;
  font-size: 1rem;
}

.section-heading button {
  min-width: 92px;
  height: 30px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.achievements-panel ul {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 18px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.achievements-panel li {
  min-width: 0;
  min-height: 58px;
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.achievement-badge {
  width: 34px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 2px solid currentColor;
  border-radius: 10px;
  font-weight: 900;
}

.achievement-general {
  color: #715cff;
  background: #eeeaff;
}

.achievement-weekly {
  color: #009b84;
  background: #e2faf4;
}

.achievement-monthly {
  color: #2b87d9;
  background: #e5f3ff;
}

.achievement-yearly {
  color: #c89200;
  background: #fff3d2;
}

.achievements-panel li div {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.achievements-panel strong,
.achievements-panel small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.achievements-panel small,
.achievements-panel time {
  color: #8d91a1;
  font-size: 0.75rem;
}

.sessions-panel {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
}

.sessions-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.sessions-summary article {
  min-height: 82px;
  display: grid;
  align-content: center;
  gap: 5px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 12px;
  color: #715cff;
  text-align: center;
}

.sessions-summary strong {
  font-size: 1.5rem;
  line-height: 1;
}

.sessions-summary span {
  font-size: 0.84rem;
}

.sessions-recent {
  min-width: 0;
}

.sessions-recent h2 {
  margin: 0 0 12px;
  font-size: 1rem;
}

.sessions-recent ul {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
}

.sessions-recent li {
  min-height: 40px;
  display: grid;
  grid-template-columns: 20px minmax(120px, 1fr) 100px auto;
  gap: 8px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.session-dot {
  width: 14px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #f2b705;
}

.session-completed {
  background: #3f6df6;
}

.session-in_progress {
  background: #00bf63;
}

.session-interrupted {
  background: #ff2d3b;
}

.sessions-recent small,
.sessions-recent time {
  color: #a0a4b2;
  font-size: 0.75rem;
}

.invitations-panel {
  max-width: 760px;
  margin-top: 30px;
}

.invitations-panel h2 {
  margin: 0 0 12px;
  font-size: 1rem;
}

.invitations-panel ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.invitations-panel li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
  padding: 8px 0;
}

.invitations-panel li div:first-child {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.invitations-panel span {
  color: #715cff;
  font-size: 0.9rem;
}

.invitation-actions {
  display: flex;
  gap: 8px;
}

.invitation-actions button {
  min-width: 88px;
  height: 30px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.invitation-actions .reject-button {
  background: #ff2d3b;
}

.invitation-actions button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.dashboard-grid {
  margin-top: 34px;
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(280px, 0.95fr);
  gap: 46px;
}

.panel h2 {
  margin: 0 0 24px;
  font-size: 1rem;
}

.task-list,
.activity-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.task-list li,
.activity-list li {
  min-height: 44px;
  display: grid;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.task-list li {
  grid-template-columns: 34px minmax(0, 1fr) auto;
  gap: 8px;
}

.activity-list li {
  grid-template-columns: 28px minmax(0, 1fr) 112px;
  gap: 8px;
}

.task-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-list time,
.activity-list small {
  color: #aeb0bb;
  font-size: 0.75rem;
}

.alert-icon {
  width: 26px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 3px solid #715cff;
  border-radius: 50%;
  color: #715cff;
  font-weight: 800;
}

.activity-dot {
  width: 20px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #f2b705;
}

.activity-dot.status-pending {
  background: #f2b705;
}

.activity-dot.status-progress {
  background: #00bf63;
}

.activity-dot.status-completed {
  background: #3f6df6;
}

.activity-dot.status-cancelled {
  background: #ff2d3b;
}

.empty-row,
.dashboard-error,
.loading-copy {
  color: #6d7180;
}

.dashboard-error {
  color: #e5333f;
}

@media (max-width: 1180px) {
  .dashboard-lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .dashboard-frame {
    grid-template-columns: 1fr;
  }

  .dashboard-content {
    padding: 28px 20px 36px;
  }

  .stats-row,
  .dashboard-grid,
  .dashboard-lower-grid,
  .sessions-summary,
  .achievements-panel ul {
    grid-template-columns: 1fr;
  }

  .achievements-panel li,
  .sessions-recent li {
    grid-template-columns: 20px minmax(0, 1fr);
  }

  .achievements-panel time,
  .sessions-recent small,
  .sessions-recent time {
    grid-column: 2;
  }
}
</style>
