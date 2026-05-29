<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Task } from './types'

const props = defineProps<{
  tasks: Task[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'create-task': []
  'view-task': [task: Task]
  'edit-task': [task: Task]
  'delete-task': [task: Task]
}>()

const orderedTasks = computed(() =>
  [...props.tasks].sort((a, b) => {
    const first = a.due_date || '9999-12-31'
    const second = b.due_date || '9999-12-31'
    return first.localeCompare(second) || a.title.localeCompare(b.title)
  }),
)

const totalTasks = computed(() => props.tasks.length)
const pendingTasks = computed(() => props.tasks.filter((task) => task.status === 'PENDING').length)
const inProgressTasks = computed(() => props.tasks.filter((task) => task.status === 'IN_PROGRESS').length)
const completedTasks = computed(() => props.tasks.filter((task) => task.status === 'COMPLETED').length)

function priorityLabel(priority: Task['priority']) {
  return {
    LOW: 'BAJA',
    MEDIUM: 'MEDIA',
    HIGH: 'ALTA',
  }[priority]
}

function priorityClass(priority: Task['priority']) {
  return {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
  }[priority]
}

function statusLabel(status: Task['status']) {
  return {
    PENDING: 'PENDIENTE',
    IN_PROGRESS: 'EN PROGRESO',
    COMPLETED: 'COMPLETADA',
    CANCELLED: 'CANCELADA',
  }[status]
}

function statusClass(status: Task['status']) {
  return {
    PENDING: 'status-pending',
    IN_PROGRESS: 'status-progress',
    COMPLETED: 'status-completed',
    CANCELLED: 'status-cancelled',
  }[status]
}

function formatDate(value: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}

function collaboratorsLabel(task: Task) {
  const collaborators = task.collaborators || []
  if (!collaborators.length) return ''
  const names = collaborators.map((collaborator) => collaborator.username)
  if (names.length <= 2) return names.join(', ')
  return `${names.slice(0, 2).join(', ')} +${names.length - 2}`
}
</script>

<template>
  <section class="tasks-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="tasks-content">
      <header class="tasks-header">
        <div>
          <h1>Mis tareas</h1>
          <div class="task-stats" aria-label="Resumen de tareas">
            <span>Todas <strong class="accent">{{ totalTasks }}</strong></span>
            <span>Pendientes <strong class="danger">{{ pendingTasks }}</strong></span>
            <span>En progreso <strong class="warning">{{ inProgressTasks }}</strong></span>
            <span>Completadas <strong class="success">{{ completedTasks }}</strong></span>
          </div>
        </div>

        <div class="header-actions">
          <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
            <span>{{ props.initials }}</span>
          </button>
          <button class="new-task-button" type="button" @click="emit('create-task')">
            <span aria-hidden="true">+</span>
            Nueva tarea
          </button>
        </div>
      </header>

      <p v-if="props.message" class="task-message">{{ props.message }}</p>
      <p v-else-if="props.loading" class="task-message">Cargando tareas...</p>

      <div class="task-table" role="table" aria-label="Listado de tareas">
        <div class="task-row task-row-head" role="row">
          <span></span>
          <strong>Tarea</strong>
          <strong>PRIORIDAD</strong>
          <strong>ESTADO</strong>
          <strong>Colaborador</strong>
          <strong>Fecha</strong>
          <span></span>
        </div>

        <div v-for="task in orderedTasks" :key="task.id" class="task-row" role="row">
          <input
            class="task-checkbox"
            type="checkbox"
            :checked="task.status === 'COMPLETED'"
            disabled
            aria-label="Estado de tarea"
          />
          <button class="task-title-button" type="button" @click="emit('view-task', task)">
            {{ task.title }}
          </button>
          <strong class="priority" :class="priorityClass(task.priority)">
            {{ priorityLabel(task.priority) }}
          </strong>
          <strong class="task-status" :class="statusClass(task.status)">
            {{ statusLabel(task.status) }}
          </strong>
          <span class="collaborator-cell" :class="{ empty: !collaboratorsLabel(task) }">
            {{ collaboratorsLabel(task) || 'Sin colaboradores' }}
          </span>
          <time>{{ formatDate(task.due_date) }}</time>
          <div class="row-actions">
            <button v-if="task.can_edit" class="icon-button" type="button" title="Editar tarea" @click="emit('edit-task', task)">
              <img src="/icono-editar.png" alt="" aria-hidden="true" />
            </button>
            <button v-if="task.is_owner" class="icon-button" type="button" title="Eliminar tarea" @click="emit('delete-task', task)">
              <img src="/icono-borrar.png" alt="" aria-hidden="true" />
            </button>
          </div>
        </div>

        <p v-if="!props.loading && !orderedTasks.length" class="empty-state">Aun no tienes tareas.</p>
      </div>
    </section>
  </section>
</template>

<style scoped>
.tasks-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.tasks-content {
  min-width: 0;
  padding: 54px 24px 74px 52px;
}

.tasks-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: start;
}

.tasks-header h1 {
  margin: 0 0 34px;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.task-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  align-items: center;
  font-size: 0.88rem;
}

.task-stats strong {
  margin-left: 10px;
  font-size: 1.2rem;
}

.accent {
  color: #715cff;
}

.danger,
.low {
  color: #ff2d3b;
}

.warning,
.medium {
  color: #ffd43b;
}

.success {
  color: #3f6df6;
}

.high {
  color: #00bf63;
}

.header-actions {
  display: grid;
  justify-items: end;
  gap: 54px;
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

.new-task-button {
  min-width: 134px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.new-task-button span {
  font-weight: 800;
}

.task-message,
.empty-state {
  color: #6d7180;
}

.task-message {
  margin: 18px 0 0;
}

.task-table {
  width: 100%;
  margin-top: 34px;
}

.task-row {
  min-height: 41px;
  display: grid;
  grid-template-columns: 34px minmax(220px, 1fr) minmax(120px, 0.25fr) minmax(140px, 0.28fr) minmax(180px, 0.38fr) minmax(120px, 0.24fr) 112px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.task-row-head {
  min-height: 25px;
}

.task-row-head strong {
  text-align: center;
  font-size: 1rem;
}

.task-row-head strong:first-of-type {
  text-align: left;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  appearance: none;
  border: 1.5px solid #00a8a8;
  border-radius: 4px;
  background: #fff;
}

.task-checkbox:checked {
  background:
    linear-gradient(45deg, transparent 45%, #00a8a8 46% 55%, transparent 56%) center / 14px 14px no-repeat;
}

.task-title-button {
  min-width: 0;
  border: 0;
  background: transparent;
  padding: 0 12px 0 0;
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.priority,
.task-status,
.collaborator-cell,
.task-row time {
  text-align: center;
}

.collaborator-cell {
  min-width: 0;
  overflow: hidden;
  color: #715cff;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collaborator-cell.empty {
  color: #9a9daa;
  font-weight: 500;
}

.status-pending {
  color: #f2b705;
}

.status-progress {
  color: #00bf63;
}

.status-completed {
  color: #3f6df6;
}

.status-cancelled {
  color: #ff2d3b;
}

.row-actions {
  display: flex;
  justify-content: end;
  gap: 8px;
}

.icon-button {
  width: 38px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.icon-button img {
  width: 34px;
  height: 34px;
  display: block;
  object-fit: contain;
}

@media (max-width: 860px) {
  .tasks-frame {
    grid-template-columns: 1fr;
  }

  .tasks-content {
    padding: 28px 16px 74px;
  }

  .tasks-header {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-items: start;
    gap: 16px;
  }

  .task-table {
    overflow-x: auto;
  }

  .task-row {
    min-width: 900px;
  }
}
</style>
