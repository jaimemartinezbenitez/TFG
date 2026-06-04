<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaMisTareas.vue"
Descripcion: Representa el listado general de tareas del usuario.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Project, Task } from './types'

const props = defineProps<{
  tasks: Task[]
  projects: Project[]
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
const highPriorityTasks = computed(() => props.tasks.filter((task) => task.priority === 'HIGH').length)

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

function projectName(task: Task) {
  if (!task.project) return 'Sin proyecto'
  return props.projects.find((project) => project.id === task.project)?.name || 'Sin proyecto'
}

function collaboratorsLabel(task: Task) {
  const collaborators = task.collaborators || []
  if (!collaborators.length) return ''
  const names = collaborators.map((collaborator) => collaborator.username)
  if (names.length <= 2) return names.join(', ')
  return `${names.slice(0, 2).join(', ')} +${names.length - 2}`
}

function createdByLabel(task: Task) {
  return task.created_by || task.owner?.username || 'Sin usuario'
}

function developedByLabel(task: Task) {
  const developers = task.developed_by?.length ? task.developed_by : []
  if (!developers.length) return 'Sin usuario'
  if (developers.length <= 2) return developers.join(', ')
  return `${developers.slice(0, 2).join(', ')} +${developers.length - 2}`
}

function ownershipLabel(task: Task) {
  if (task.is_owner) return 'Propia'
  if (task.collaboration_role) return `Compartida · ${task.collaboration_role}`
  return 'Tarea'
}
</script>

<template>
  <section class="tasks-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="tasks-content">
      <header class="tasks-header">
        <div>
          <h1>Mis tareas</h1>
          <p>Organiza, revisa y prioriza el trabajo activo.</p>
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

      <div class="task-stats" aria-label="Resumen de tareas">
        <article>
          <span>Total</span>
          <strong class="accent">{{ totalTasks }}</strong>
        </article>
        <article>
          <span>Pendientes</span>
          <strong class="danger">{{ pendingTasks }}</strong>
        </article>
        <article>
          <span>En progreso</span>
          <strong class="warning">{{ inProgressTasks }}</strong>
        </article>
        <article>
          <span>Alta prioridad</span>
          <strong class="success">{{ highPriorityTasks }}</strong>
        </article>
        <article>
          <span>Completadas</span>
          <strong class="accent">{{ completedTasks }}</strong>
        </article>
      </div>

      <div class="task-table-shell">
      <div class="task-table" role="table" aria-label="Listado de tareas">
        <div class="task-row task-row-head" role="row">
          <span></span>
          <strong>Tarea</strong>
          <strong>Prioridad</strong>
          <strong>Estado</strong>
          <strong>Entrega</strong>
          <span></span>
        </div>

        <div v-for="task in orderedTasks" :key="task.id" class="task-row" role="row">
          <span class="task-state-dot" :class="statusClass(task.status)" aria-hidden="true"></span>
          <div class="task-main-cell">
            <button class="task-title-button" type="button" @click="emit('view-task', task)">
              {{ task.title }}
            </button>
            <div class="task-meta">
              <span>{{ projectName(task) }}</span>
              <span>{{ ownershipLabel(task) }}</span>
              <span>{{ collaboratorsLabel(task) || 'Sin colaboradores' }}</span>
            </div>
            <small>Creada por {{ createdByLabel(task) }} · Desarrollada por {{ developedByLabel(task) }}</small>
          </div>
          <strong class="priority badge" :class="priorityClass(task.priority)">
            {{ priorityLabel(task.priority) }}
          </strong>
          <strong class="task-status badge" :class="statusClass(task.status)">
            {{ statusLabel(task.status) }}
          </strong>
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
  padding: 62px 24px 74px 52px;
}

.tasks-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: start;
}

.tasks-header h1 {
  margin: 0 0 8px;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

.tasks-header p {
  margin: 0;
  color: #6d7180;
  font-size: 1.04rem;
}

.task-stats {
  width: min(100%, 980px);
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(5, minmax(118px, 1fr));
  gap: 12px;
}

.task-stats article {
  min-height: 78px;
  display: grid;
  align-content: center;
  gap: 6px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fbfffe;
  padding: 12px 14px;
}

.task-stats span {
  color: #6d7180;
  font-size: 0.82rem;
}

.task-stats strong {
  font-size: 1.55rem;
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

.task-table-shell {
  width: min(100%, 1180px);
  margin-top: 22px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.task-table {
  width: 100%;
}

.task-row {
  min-height: 76px;
  display: grid;
  grid-template-columns: 34px minmax(300px, 1fr) 112px 132px 112px 104px;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
  padding: 0 18px;
}

.task-row-head {
  min-height: 42px;
  background: #fbfffe;
}

.task-row-head strong {
  color: #565b6a;
  text-align: left;
  font-size: 0.82rem;
  text-transform: uppercase;
}

.task-row-head strong:nth-of-type(n + 2) {
  text-align: center;
}

.task-state-dot {
  width: 16px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: currentColor;
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
  font-size: 1rem;
  font-weight: 800;
}

.task-main-cell {
  min-width: 0;
  display: grid;
  gap: 5px;
}

.task-meta {
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.task-meta span {
  max-width: 180px;
  min-width: 0;
  overflow: hidden;
  border: 1px solid #d5f6ef;
  border-radius: 999px;
  color: #715cff;
  padding: 3px 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.78rem;
}

.task-main-cell small {
  min-width: 0;
  overflow: hidden;
  color: #8d91a1;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.78rem;
}

.badge,
.task-row time {
  text-align: center;
}

.badge {
  justify-self: center;
  min-width: 88px;
  border-radius: 999px;
  padding: 6px 10px;
  background: #f7f8ff;
  font-size: 0.78rem;
}

.priority.low {
  color: #3f6df6;
  background: #edf3ff;
}

.priority.medium {
  color: #c89200;
  background: #fff7df;
}

.priority.high {
  color: #ff2d3b;
  background: #ffecef;
}

.status-pending {
  color: #f2b705;
  background: #fff7df;
}

.status-progress {
  color: #00bf63;
  background: #e8fbf4;
}

.status-completed {
  color: #3f6df6;
  background: #edf3ff;
}

.status-cancelled {
  color: #ff2d3b;
  background: #ffecef;
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
    min-width: 860px;
  }

  .task-stats {
    grid-template-columns: 1fr;
  }
}
</style>
