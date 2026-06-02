<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { CalendarData, CalendarItem, Task } from './types'

const props = defineProps<{
  calendar: CalendarData | null
  tasks: Task[]
  selectedDate: string
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'change-month': [date: string]
  'open-item': [item: CalendarItem]
}>()

const weekDays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

function parseIsoDate(value: string) {
  return new Date(`${value}T00:00:00`)
}

function toIsoDate(date: Date) {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localDate.toISOString().slice(0, 10)
}

const monthStart = computed(() => {
  const base = props.calendar?.start_date || props.selectedDate
  const date = parseIsoDate(base)
  return new Date(date.getFullYear(), date.getMonth(), 1)
})

const monthLabel = computed(() => {
  const formatter = new Intl.DateTimeFormat('es-ES', { month: 'long', year: 'numeric' })
  const label = formatter.format(monthStart.value)
  return label.charAt(0).toUpperCase() + label.slice(1)
})

const currentMonth = computed(() => monthStart.value.getMonth())

const itemsByDate = computed(() => {
  const map = new Map<string, CalendarItem[]>()
  for (const item of props.calendar?.items || []) {
    const dateItems = map.get(item.date) || []
    dateItems.push(item)
    map.set(item.date, dateItems)
  }
  return map
})

const upcomingDueTasks = computed(() =>
  props.tasks
    .filter((task) => task.due_date && task.status !== 'COMPLETED' && task.status !== 'CANCELLED')
    .sort((a, b) => (a.due_date || '').localeCompare(b.due_date || ''))
    .slice(0, 5),
)

const calendarDays = computed(() => {
  const start = new Date(monthStart.value)
  const mondayOffset = (start.getDay() + 6) % 7
  start.setDate(start.getDate() - mondayOffset)

  const daysInMonth = new Date(monthStart.value.getFullYear(), monthStart.value.getMonth() + 1, 0).getDate()
  const visibleWeeks = Math.ceil((mondayOffset + daysInMonth) / 7)
  const totalCells = visibleWeeks * 7

  return Array.from({ length: totalCells }, (_, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    const isoDate = toIsoDate(date)
    return {
      isoDate,
      dayNumber: date.getDate(),
      isCurrentMonth: date.getMonth() === currentMonth.value,
      items: itemsByDate.value.get(isoDate) || [],
    }
  })
})

function moveMonth(offset: number) {
  const target = new Date(monthStart.value)
  target.setMonth(target.getMonth() + offset)
  emit('change-month', toIsoDate(target))
}

function itemLabel(item: CalendarItem) {
  if (item.type === 'project_start') return `Inicio: ${item.title}`
  if (item.type === 'project_end') return `Fin: ${item.title}`
  return item.title
}

function taskStatusLabel(status: Task['status']) {
  return {
    PENDING: 'PENDIENTE',
    IN_PROGRESS: 'EN PROGRESO',
    COMPLETED: 'COMPLETADA',
    CANCELLED: 'CANCELADA',
  }[status]
}

function formatDate(value: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}

function itemClass(item: CalendarItem) {
  if (item.type !== 'task') return 'project-item'
  return {
    PENDING: 'task-pending',
    IN_PROGRESS: 'task-progress',
    COMPLETED: 'task-completed',
    CANCELLED: 'task-cancelled',
  }[item.status || 'PENDING']
}
</script>

<template>
  <section class="calendar-frame">
    <MenuLateral active="calendario" @navigate="emit('navigate', $event)" />

    <section class="calendar-content">
      <header class="calendar-page-header">
        <h1>Calendario</h1>
        <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
          <span>{{ props.initials }}</span>
        </button>
      </header>

      <p v-if="props.message" class="calendar-message">{{ props.message }}</p>
      <p v-else-if="props.loading" class="calendar-message">Cargando calendario...</p>

      <div class="calendar-layout">
      <section class="calendar-board" aria-label="Calendario mensual">
        <header class="month-header">
          <h2>{{ monthLabel }}</h2>
          <div class="month-actions">
            <button type="button" title="Mes anterior" @click="moveMonth(-1)">‹</button>
            <button type="button" title="Mes siguiente" @click="moveMonth(1)">›</button>
          </div>
        </header>

        <div class="weekday-row">
          <strong v-for="day in weekDays" :key="day">{{ day }}</strong>
        </div>

        <div class="calendar-grid">
          <article
            v-for="day in calendarDays"
            :key="day.isoDate"
            class="calendar-day"
            :class="{ muted: !day.isCurrentMonth }"
          >
            <span class="day-number">{{ day.dayNumber }}</span>
            <div class="day-items">
              <button
                v-for="item in day.items"
                :key="`${item.type}-${item.id}-${item.date}`"
                class="calendar-item"
                :class="itemClass(item)"
                type="button"
                @click="emit('open-item', item)"
              >
                {{ itemLabel(item) }}
              </button>
            </div>
          </article>
        </div>
      </section>

      <aside class="upcoming-panel" aria-label="Tareas que vencen pronto">
        <h2>Tareas que vencen pronto</h2>
        <ul>
          <li v-for="task in upcomingDueTasks" :key="task.id">
            <button type="button" @click="emit('open-item', { id: task.id, type: 'task', title: task.title, date: task.due_date || '', status: task.status })">
              <strong>{{ task.title }}</strong>
              <span>{{ formatDate(task.due_date) }}</span>
              <small :class="itemClass({ id: task.id, type: 'task', title: task.title, date: task.due_date || '', status: task.status })">
                {{ taskStatusLabel(task.status) }}
              </small>
            </button>
          </li>
          <li v-if="!upcomingDueTasks.length" class="empty-upcoming">No hay tareas próximas.</li>
        </ul>
      </aside>
      </div>
    </section>
  </section>
</template>

<style scoped>
.calendar-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.calendar-content {
  position: relative;
  min-width: 0;
  padding: 62px 42px 74px;
}

.calendar-page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.calendar-page-header h1 {
  margin: 0 0 4px;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
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

.calendar-message {
  margin: 0 0 12px;
  color: #6d7180;
}

.calendar-layout {
  margin-top: 0;
  display: grid;
  grid-template-columns: minmax(640px, 1fr) minmax(240px, 320px);
  gap: 28px;
  align-items: start;
}

.calendar-board {
  width: 100%;
  margin-top: 0;
  border: 2px solid #2f82e8;
  background: #fff;
}

.month-header {
  min-height: 62px;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 0 14px;
  color: #fff;
  background: #6759f6;
}

.month-header h2 {
  margin: 0;
  font-size: clamp(2rem, 3.8vw, 2.35rem);
  line-height: 1;
}

.month-actions {
  display: flex;
  gap: 6px;
}

.month-actions button {
  width: 32px;
  height: 34px;
  border: 0;
  background: transparent;
  color: #fff;
  font-size: 2.8rem;
  line-height: 0.8;
  cursor: pointer;
}

.weekday-row,
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}

.weekday-row strong {
  min-height: 38px;
  display: grid;
  place-items: center;
  border-right: 2px solid #2f82e8;
  border-bottom: 2px solid #2f82e8;
  color: #6759f6;
  font-size: 0.92rem;
}

.weekday-row strong:last-child {
  border-right: 0;
}

.calendar-day {
  position: relative;
  min-height: 104px;
  border-right: 2px solid #2f82e8;
  border-bottom: 2px solid #2f82e8;
  padding: 22px 7px 6px;
  overflow: hidden;
}

.calendar-day:nth-child(7n) {
  border-right: 0;
}

.calendar-day:nth-last-child(-n + 7) {
  border-bottom: 0;
}

.calendar-day.muted {
  background: #fafbff;
  color: #aeb0bb;
}

.day-number {
  position: absolute;
  top: 3px;
  right: 4px;
  color: #2f82e8;
  font-size: 0.76rem;
  font-weight: 700;
}

.day-items {
  display: grid;
  gap: 3px;
}

.calendar-item {
  min-height: 24px;
  border: 1.5px solid currentColor;
  border-radius: 3px;
  background: #fff;
  padding: 2px 4px;
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.68rem;
  font-weight: 800;
  cursor: pointer;
}

.task-pending {
  color: #f2b705;
}

.task-progress,
.project-item {
  color: #00bf63;
}

.task-completed {
  color: #3f6df6;
}

.task-cancelled {
  color: #ff2d3b;
}

.upcoming-panel {
  border-left: 4px solid #715cff;
  padding-left: 18px;
}

.upcoming-panel h2 {
  margin: 0 0 16px;
  font-size: 1.15rem;
}

.upcoming-panel ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.upcoming-panel button {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 4px 10px;
  border: 0;
  border-bottom: 1px solid #75ddcb;
  padding: 8px 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.upcoming-panel strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upcoming-panel span {
  color: #6d7180;
  font-size: 0.85rem;
}

.upcoming-panel small {
  grid-column: 1 / -1;
  font-weight: 800;
}

.empty-upcoming {
  color: #6d7180;
}

@media (max-width: 960px) {
  .calendar-layout {
    grid-template-columns: 1fr;
  }

  .calendar-board {
    overflow-x: auto;
  }

  .weekday-row,
  .calendar-grid,
  .month-header {
    min-width: 920px;
  }
}

@media (max-width: 860px) {
  .calendar-frame {
    grid-template-columns: 1fr;
  }

  .calendar-content {
    padding: 82px 16px 74px;
  }
}
</style>
