<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaEstadisticas.vue"
Descripcion: Representa el panel de estadísticas y métricas de productividad.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type {
  DashboardData,
  ProductivitySession,
  ProductivityTechnique,
  Project,
  StatisticsPeriod,
  Task,
} from './types'

const props = defineProps<{
  initials: string
  tasks: Task[]
  projects: Project[]
  sessions: ProductivitySession[]
  dashboard: DashboardData | null
  period: StatisticsPeriod
  selectedDate: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'change-period': [period: StatisticsPeriod, date: string]
}>()

const periodOptions: Array<{ value: StatisticsPeriod; label: string }> = [
  { value: 'day', label: 'Diario' },
  { value: 'week', label: 'Semanal' },
  { value: 'month', label: 'Mensual' },
]

const techniqueColors: Record<ProductivityTechnique, string> = {
  POMODORO: '#715cff',
  TIME_BLOCKING: '#5fc18b',
  FIFTY_TWO_SEVENTEEN: '#ffa94d',
}

const selectedPeriod = computed(() => props.dashboard?.period?.view ?? props.period)
const selectedDateValue = computed(() => props.dashboard?.period?.selected_date ?? props.selectedDate)
const summary = computed(() => props.dashboard?.summary)
const completedTasks = computed(() => props.tasks.filter((task) => task.status === 'COMPLETED'))
const completedSessions = computed(() => props.sessions.filter((session) => session.status === 'COMPLETED'))

const completedTasksCount = computed(() => summary.value?.tasks_completed ?? completedTasks.value.length)
const activeProjects = computed(() => summary.value?.active_projects ?? props.projects.length)
const totalFocusMinutes = computed(() => {
  if (typeof summary.value?.effective_minutes === 'number') return summary.value.effective_minutes
  return completedSessions.value.reduce((total, session) => total + session.effective_time, 0)
})
const totalRegisteredMinutes = computed(() => {
  if (typeof summary.value?.registered_time === 'number') return summary.value.registered_time
  return completedSessions.value.reduce((total, session) => total + session.total_duration, 0)
})
const totalBreakMinutes = computed(() => {
  if (typeof summary.value?.break_minutes === 'number') return summary.value.break_minutes
  return completedSessions.value.reduce(
    (total, session) => total + Math.max(session.total_duration - session.effective_time, 0),
    0,
  )
})
const productivityPercentage = computed(() => {
  if (typeof summary.value?.productivity_percentage === 'number') return summary.value.productivity_percentage
  if (totalRegisteredMinutes.value > 0) {
    return Math.round((totalFocusMinutes.value / totalRegisteredMinutes.value) * 100)
  }
  const usefulTasks = props.tasks.filter((task) => task.status !== 'CANCELLED').length
  return usefulTasks ? Math.round((completedTasks.value.length / usefulTasks) * 100) : 0
})
const consecutiveDays = computed(() => summary.value?.consecutive_days ?? fallbackConsecutiveDays())

const periodRangeLabel = computed(() => {
  const period = props.dashboard?.period
  if (!period) return 'Datos reales de la API'
  return `${formatDate(period.start_date)} - ${formatDate(period.end_date)}`
})

const chartTitle = computed(() => {
  if (selectedPeriod.value === 'day') return 'Tiempo de enfoque por franjas horarias'
  if (selectedPeriod.value === 'month') return 'Tiempo de enfoque por dia del mes'
  return 'Tiempo de enfoque por dia'
})

const periodLabel = computed(() => {
  return periodOptions.find((option) => option.value === selectedPeriod.value)?.label ?? 'Semanal'
})

const focusSeries = computed(() => {
  if (props.dashboard?.focus_series?.length) return props.dashboard.focus_series
  return fallbackFocusSeries()
})

const focusByDay = computed(() => {
  const maxMinutes = Math.max(...focusSeries.value.map((item) => item.minutes), 60)
  return focusSeries.value.map((item) => ({
    ...item,
    height: `${Math.max((item.minutes / maxMinutes) * 100, item.minutes ? 12 : 4)}%`,
    valueLabel: durationLabel(item.minutes),
  }))
})

const barChartStyle = computed(() => ({
  gridTemplateColumns: `repeat(${Math.max(focusByDay.value.length, 1)}, minmax(${
    selectedPeriod.value === 'month' ? '38px' : '72px'
  }, 1fr))`,
}))

const techniqueDistribution = computed(() => {
  if (props.dashboard?.technique_distribution?.length) {
    return props.dashboard.technique_distribution.map((item) => ({
      technique: item.technique,
      label: item.label,
      minutes: item.minutes,
      percentage: item.percentage,
      color: techniqueColors[item.technique],
    }))
  }

  const totals = completedSessions.value.reduce<Record<ProductivityTechnique, number>>(
    (accumulator, session) => {
      accumulator[session.technique] += session.effective_time
      return accumulator
    },
    { POMODORO: 0, TIME_BLOCKING: 0, FIFTY_TWO_SEVENTEEN: 0 },
  )
  const total = Object.values(totals).reduce((sum, value) => sum + value, 0)
  return (Object.entries(totals) as Array<[ProductivityTechnique, number]>).map(([technique, minutes]) => ({
    technique,
    label: techniqueLabel(technique),
    minutes,
    percentage: total ? Math.round((minutes / total) * 100) : 0,
    color: techniqueColors[technique],
  }))
})

const donutStyle = computed(() => {
  let start = 0
  const stops = techniqueDistribution.value
    .filter((item) => item.percentage > 0)
    .map((item) => {
      const end = start + item.percentage
      const segment = `${item.color} ${start}% ${end}%`
      start = end
      return segment
    })

  if (!stops.length) return 'conic-gradient(#e9e5ff 0 100%)'
  return `conic-gradient(${stops.join(', ')})`
})

function changePeriod(period: StatisticsPeriod) {
  emit('change-period', period, selectedDateValue.value)
}

function changeDate(event: Event) {
  const input = event.target as HTMLInputElement
  emit('change-period', selectedPeriod.value, input.value)
}

function techniqueLabel(technique: ProductivityTechnique) {
  const labels = {
    POMODORO: 'Pomodoro',
    TIME_BLOCKING: 'Time Blocking',
    FIFTY_TWO_SEVENTEEN: '52/17',
  }
  return labels[technique]
}

function durationLabel(minutes: number) {
  if (!minutes) return '0m'
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (!hours) return `${remainingMinutes}m`
  if (!remainingMinutes) return `${hours}h`
  return `${hours}h ${remainingMinutes}m`
}

function formatDate(value: string) {
  if (!value) return ''
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }).format(
    new Date(`${value}T00:00:00`),
  )
}

function toIsoDate(date: Date) {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localDate.toISOString().slice(0, 10)
}

function fallbackFocusSeries() {
  const today = new Date()
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today)
    date.setDate(today.getDate() - (6 - index))
    return {
      key: toIsoDate(date),
      label: new Intl.DateTimeFormat('es-ES', { weekday: 'long' }).format(date),
      short_label: new Intl.DateTimeFormat('es-ES', { weekday: 'short' }).format(date).replace('.', ''),
      minutes: 0,
    }
  })

  const dayMap = new Map(days.map((day) => [day.key, day]))
  completedSessions.value.forEach((session) => {
    const day = dayMap.get(toIsoDate(new Date(session.start_at)))
    if (day) day.minutes += session.effective_time
  })
  return days
}

function fallbackConsecutiveDays() {
  const sessionDates = new Set(completedSessions.value.map((session) => toIsoDate(new Date(session.start_at))))
  if (!sessionDates.size) return 0
  const sortedDates = [...sessionDates].sort().reverse()
  let cursor = new Date(`${sortedDates[0]}T00:00:00`)
  let streak = 0
  while (sessionDates.has(toIsoDate(cursor))) {
    streak += 1
    cursor.setDate(cursor.getDate() - 1)
  }
  return streak
}
</script>

<template>
  <section class="statistics-frame">
    <MenuLateral active="estadisticas" @navigate="emit('navigate', $event)" />

    <section class="statistics-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <div class="statistics-header">
        <div class="statistics-title-block">
          <h1>Estadísticas</h1>
          <p class="period-copy">{{ periodLabel }} · {{ periodRangeLabel }}</p>

          <div class="period-controls" aria-label="Seleccionar periodo de estadísticas">
            <div class="period-tabs">
              <button
                v-for="option in periodOptions"
                :key="option.value"
                type="button"
                :class="{ active: selectedPeriod === option.value }"
                @click="changePeriod(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
            <input type="date" :value="selectedDateValue" @change="changeDate" />
          </div>
        </div>
      </div>

      <p v-if="props.message" class="statistics-message">{{ props.message }}</p>
      <p v-else-if="props.loading" class="loading-copy">Cargando estadísticas...</p>

      <div class="summary-cards" aria-label="Resumen estadístico">
        <article>
          <strong>{{ completedTasksCount }}</strong>
          <span>Tareas<br />completadas</span>
        </article>
        <article>
          <strong>{{ productivityPercentage }}%</strong>
          <span>Productividad</span>
        </article>
        <article>
          <strong>{{ consecutiveDays }}</strong>
          <span>Días<br />consecutivos</span>
        </article>
        <article>
          <strong>{{ durationLabel(totalFocusMinutes) }}</strong>
          <span>Tiempo total</span>
        </article>
      </div>

      <section class="statistics-grid">
        <article class="chart-panel focus-panel">
          <div class="panel-header">
            <h2>{{ chartTitle }}</h2>
            <span>{{ periodLabel }}</span>
          </div>

          <div class="bar-chart" :style="barChartStyle">
            <div v-for="item in focusByDay" :key="item.key" class="bar-column">
              <span class="bar-value">{{ item.valueLabel }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ height: item.height }"></div>
              </div>
              <small>{{ item.short_label }}</small>
              <strong>{{ item.label }}</strong>
            </div>
          </div>
        </article>

        <article class="chart-panel distribution-panel">
          <h2>Distribución de técnicas</h2>
          <div class="donut-row">
            <div class="donut" :style="{ background: donutStyle }" aria-hidden="true"></div>
            <ul>
              <li v-for="item in techniqueDistribution" :key="item.technique">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <strong>{{ item.label }}</strong>
                <small>{{ item.percentage }}%</small>
              </li>
            </ul>
          </div>
        </article>

        <article class="chart-panel weekly-panel">
          <h2>Resumen del periodo</h2>
          <ul>
            <li>
              <span>Tareas completadas</span>
              <strong>{{ completedTasksCount }}</strong>
            </li>
            <li>
              <span>Proyectos activos</span>
              <strong>{{ activeProjects }}</strong>
            </li>
            <li>
              <span>Tiempo de descanso</span>
              <strong>{{ durationLabel(totalBreakMinutes) }}</strong>
            </li>
            <li>
              <span>Tiempo registrado</span>
              <strong>{{ durationLabel(totalRegisteredMinutes || totalFocusMinutes) }}</strong>
            </li>
            <li>
              <span>Productividad promedio</span>
              <strong>{{ productivityPercentage }}%</strong>
            </li>
          </ul>
        </article>
      </section>
    </section>
  </section>
</template>

<style scoped>
.statistics-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.statistics-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 88px 48px 64px 32px;
}

.avatar-button {
  position: absolute;
  top: 10px;
  right: 24px;
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

.statistics-header,
.statistics-message,
.loading-copy,
.summary-cards,
.statistics-grid {
  width: min(100%, 1220px);
}

.statistics-header {
  display: block;
}

.statistics-title-block {
  max-width: 760px;
}

h1 {
  margin: 0;
  font-size: clamp(2.8rem, 5vw, 4rem);
  line-height: 1;
}

.period-copy {
  margin: 10px 0 0;
  color: #565b6c;
  font-size: 1rem;
}

.period-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  align-items: center;
  justify-content: flex-start;
  margin-top: 18px;
}

.period-tabs {
  display: inline-flex;
  gap: 8px;
  margin-right: 0 !important;
  margin-left: 0 !important;
  padding: 4px;
  border: 2px solid #715cff;
  border-radius: 999px;
}

.period-tabs button {
  min-width: 86px;
  height: 34px;
  border: 0;
  border-radius: 999px;
  color: #715cff;
  background: #fff;
  font-weight: 800;
  cursor: pointer;
}

.period-tabs button.active {
  color: #fff;
  background: #715cff;
}

.period-controls input {
  height: 34px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 0 10px;
  font: inherit;
}

.statistics-message,
.loading-copy {
  color: #6d7180;
}

.statistics-message {
  color: #e5333f;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(170px, 1fr));
  gap: 18px;
  margin-top: 28px;
}

.summary-cards article {
  min-height: 190px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 12px;
  border: 2px solid #715cff;
  border-radius: 8px;
  color: #715cff;
  text-align: center;
}

.summary-cards strong {
  font-size: clamp(2.4rem, 4vw, 3.3rem);
  line-height: 1;
}

.summary-cards span {
  font-size: 1.1rem;
}

.statistics-grid {
  display: grid;
  grid-template-columns: minmax(520px, 1.55fr) minmax(340px, 0.95fr);
  gap: 20px;
  margin-top: 30px;
  align-items: stretch;
}

.focus-panel {
  grid-row: span 2;
  overflow-x: auto;
}

.chart-panel {
  min-width: 0;
  border: 1px solid #f0f0f2;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 4px 14px rgb(15 20 48 / 6%);
}

.chart-panel h2 {
  margin: 0;
  font-size: 1.2rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}

.panel-header span {
  border: 1px solid #e3e5ee;
  border-radius: 5px;
  padding: 6px 12px;
  color: #4f5360;
  font-size: 0.9rem;
}

.bar-chart {
  min-width: 100%;
  height: 390px;
  display: grid;
  gap: 18px;
  align-items: end;
  margin-top: 22px;
}

.bar-column {
  height: 100%;
  min-width: 0;
  display: grid;
  grid-template-rows: 28px 1fr 22px 42px;
  gap: 8px;
  justify-items: center;
  color: #303443;
  text-align: center;
}

.bar-value {
  color: #715cff;
  font-size: 0.92rem;
  font-weight: 800;
}

.bar-track {
  width: 100%;
  display: flex;
  align-items: end;
  border-bottom: 1px solid #e7e2ff;
}

.bar-fill {
  width: min(100%, 38px);
  margin: 0 auto;
  border-radius: 7px 7px 0 0;
  background: linear-gradient(180deg, #715cff, #4b31db);
}

.bar-column small {
  color: #8c91a4;
  font-size: 0.9rem;
  text-transform: capitalize;
}

.bar-column strong {
  width: 100%;
  color: #303443;
  font-size: 0.88rem;
  line-height: 1.1;
  text-transform: capitalize;
  white-space: normal;
}

.donut-row {
  display: grid;
  grid-template-columns: 170px minmax(0, 1fr);
  gap: 24px;
  align-items: center;
  margin-top: 24px;
}

.donut {
  width: 170px;
  aspect-ratio: 1;
  border-radius: 50%;
  position: relative;
}

.donut::after {
  content: "";
  position: absolute;
  inset: 44px;
  border-radius: 50%;
  background: #fff;
}

.distribution-panel ul,
.weekly-panel ul {
  display: grid;
  gap: 14px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.distribution-panel li,
.weekly-panel li {
  min-width: 0;
  display: grid;
  align-items: center;
  gap: 10px;
  color: #303443;
  font-size: 1rem;
}

.distribution-panel li {
  grid-template-columns: 14px minmax(0, 1fr) 52px;
}

.weekly-panel li {
  grid-template-columns: minmax(0, 1fr) auto;
}

.legend-dot {
  width: 12px;
  aspect-ratio: 1;
  border-radius: 50%;
}

.distribution-panel strong,
.weekly-panel span {
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
}

.distribution-panel small {
  color: #715cff;
  font-weight: 900;
  text-align: right;
}

.weekly-panel strong {
  color: #0d1430;
  white-space: nowrap;
}

@media (max-width: 1180px) {
  .statistics-header {
    align-items: start;
    flex-direction: column;
  }

  .period-controls {
    justify-items: start;
  }

  .statistics-grid {
    grid-template-columns: 1fr;
  }

  .focus-panel {
    grid-row: auto;
  }
}

@media (max-width: 860px) {
  .statistics-frame {
    grid-template-columns: 1fr;
  }

  .statistics-content {
    padding: 82px 20px 48px;
  }

  .summary-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .period-tabs {
    width: 100%;
    flex-wrap: wrap;
  }

  .period-tabs button,
  .period-controls input {
    width: 100%;
  }

  .bar-chart {
    height: auto;
    grid-template-columns: 1fr !important;
  }

  .bar-column {
    grid-template-columns: 90px minmax(0, 1fr) 70px;
    grid-template-rows: auto;
    align-items: center;
    text-align: left;
  }

  .bar-track {
    height: 34px;
    align-items: center;
    border-bottom: 0;
  }

  .bar-fill {
    height: 16px !important;
    width: 100%;
  }

  .bar-column strong {
    display: none;
  }

  .donut-row {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}
</style>
