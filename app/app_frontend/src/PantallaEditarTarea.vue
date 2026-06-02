<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Project, Task, TaskForm } from './types'

const props = defineProps<{
  task: Task | null
  form: TaskForm
  projects: Project[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  submit: []
  cancel: []
}>()

const selectedProjectName = computed(() => {
  const projectId = props.form.project ? Number(props.form.project) : props.task?.project
  if (!projectId) return 'Sin proyecto'
  return props.projects.find((project) => project.id === projectId)?.name || 'Sin proyecto'
})

const collaboratorsLabel = computed(() => {
  const collaborators = props.task?.collaborators || []
  if (!collaborators.length) return 'Sin colaboradores'
  return collaborators.map((collaborator) => `${collaborator.username} (${roleLabel(collaborator.role)})`).join(', ')
})

function priorityLabel(priority: Task['priority']) {
  return {
    LOW: 'BAJA',
    MEDIUM: 'MEDIA',
    HIGH: 'ALTA',
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

function roleLabel(role: 'READER' | 'EDITOR' | 'ADMIN') {
  return {
    READER: 'Lector',
    EDITOR: 'Editor',
    ADMIN: 'Administrador',
  }[role]
}

function formatDateTime(value?: string) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(value))
}

function formatDate(value?: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}
</script>

<template>
  <section class="task-edit-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="task-edit-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <header class="edit-header">
        <div>
          <h1>Editar tarea</h1>
          <p>{{ props.task?.title || 'Tarea seleccionada' }}</p>
        </div>
      </header>

      <form class="edit-layout" @submit.prevent="emit('submit')">
        <section class="edit-panel" aria-label="Campos editables de la tarea">
          <h2>Datos editables</h2>
          <div class="form-grid">
            <label class="wide" for="taskTitle">
              Título
              <input id="taskTitle" v-model.trim="props.form.title" required maxlength="50" placeholder="Nombre de la tarea" />
            </label>

            <label class="wide" for="taskDescription">
              Descripción
              <textarea id="taskDescription" v-model.trim="props.form.description" placeholder="Describe la tarea..."></textarea>
            </label>

            <label for="taskPriority">
              Prioridad
              <select id="taskPriority" v-model="props.form.priority">
                <option value="HIGH">ALTA</option>
                <option value="MEDIUM">MEDIA</option>
                <option value="LOW">BAJA</option>
              </select>
            </label>

            <label for="taskStatus">
              Estado
              <select id="taskStatus" v-model="props.form.status">
                <option value="PENDING">PENDIENTE</option>
                <option value="IN_PROGRESS">EN PROGRESO</option>
                <option value="COMPLETED">COMPLETADA</option>
                <option value="CANCELLED">CANCELADA</option>
              </select>
            </label>

            <label for="taskDate">
              Fecha límite
              <input id="taskDate" v-model="props.form.due_date" type="date" />
            </label>

            <label for="taskProject">
              Proyecto
              <select id="taskProject" v-model="props.form.project">
                <option value="">Sin proyecto</option>
                <option v-for="project in props.projects" :key="project.id" :value="String(project.id)">
                  {{ project.name }}
                </option>
              </select>
            </label>
          </div>
        </section>

        <aside class="detail-panel" aria-label="Información actual de la tarea">
          <h2>Información de la tarea</h2>
          <dl>
            <div>
              <dt>Creada por</dt>
              <dd>{{ props.task?.created_by || props.task?.owner?.username || 'Sin usuario' }}</dd>
            </div>
            <div>
              <dt>Desarrollada por</dt>
              <dd>{{ props.task?.developed_by?.join(', ') || props.task?.owner?.username || 'Sin usuario' }}</dd>
            </div>
            <div>
              <dt>Proyecto actual</dt>
              <dd>{{ selectedProjectName }}</dd>
            </div>
            <div>
              <dt>Colaboradores</dt>
              <dd>{{ collaboratorsLabel }}</dd>
            </div>
            <div>
              <dt>Prioridad actual</dt>
              <dd>{{ priorityLabel(props.form.priority) }}</dd>
            </div>
            <div>
              <dt>Estado actual</dt>
              <dd>{{ statusLabel(props.form.status) }}</dd>
            </div>
            <div>
              <dt>Fecha de creación</dt>
              <dd>{{ formatDateTime(props.task?.created_at) }}</dd>
            </div>
            <div>
              <dt>Última actualización</dt>
              <dd>{{ formatDateTime(props.task?.updated_at) }}</dd>
            </div>
            <div>
              <dt>Fecha límite</dt>
              <dd>{{ formatDate(props.form.due_date || props.task?.due_date) }}</dd>
            </div>
          </dl>
        </aside>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <div class="form-actions">
          <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">Cancelar</button>
          <button class="save-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Guardando...' : 'Guardar tarea' }}
          </button>
        </div>
      </form>
    </section>
  </section>
</template>

<style scoped>
.task-edit-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.task-edit-content {
  position: relative;
  min-width: 0;
  padding: 62px 40px 74px 34px;
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

.edit-header {
  width: calc(100% - 90px);
}

.edit-header h1 {
  margin: 0;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

.edit-header p {
  margin: 4px 0 0;
  color: #715cff;
  font-size: 1.15rem;
  font-weight: 800;
}

.edit-layout {
  width: 100%;
  margin-top: 10px;
  display: grid;
  grid-template-columns: minmax(420px, 0.95fr) minmax(360px, 0.75fr);
  gap: 28px;
  align-items: start;
}

.edit-panel,
.detail-panel {
  min-width: 0;
}

h2 {
  margin: 0 0 14px;
  font-size: 1.28rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(180px, 1fr));
  gap: 16px;
}

label {
  min-width: 0;
  display: grid;
  gap: 7px;
  font-size: 1.02rem;
}

.wide {
  grid-column: 1 / -1;
}

input,
textarea,
select {
  width: 100%;
  border: 2px solid #7161ff;
  border-radius: 8px;
  background: #fff;
  outline: none;
}

input,
select {
  height: 34px;
  padding: 0 10px;
}

textarea {
  min-height: 156px;
  resize: vertical;
  padding: 10px;
}

input::placeholder,
textarea::placeholder {
  color: #b8bac4;
  font-style: italic;
}

select {
  cursor: pointer;
}

.detail-panel {
  border-left: 4px solid #715cff;
  padding-left: 18px;
}

.detail-panel dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(140px, 1fr));
  gap: 12px 14px;
  margin: 0;
}

.detail-panel div {
  min-width: 0;
}

.detail-panel dt {
  margin-bottom: 5px;
  font-weight: 800;
}

.detail-panel dd {
  min-height: 32px;
  display: flex;
  align-items: center;
  margin: 0;
  border: 2px solid #7161ff;
  padding: 4px 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-message {
  grid-column: 1 / -1;
  margin: 0;
  color: #e5333f;
}

.form-actions {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 170px 220px;
  justify-content: center;
  gap: 30px;
  margin-top: 4px;
}

.cancel-button,
.save-button {
  height: 34px;
  border-radius: 999px;
  cursor: pointer;
}

.cancel-button {
  border: 1.5px solid #101010;
  background: #fff;
}

.save-button {
  border: 0;
  color: #fff;
  background: #715cff;
}

.cancel-button:disabled,
.save-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

@media (max-width: 1050px) {
  .edit-layout,
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .task-edit-frame {
    grid-template-columns: 1fr;
  }

  .task-edit-content {
    padding: 82px 20px 74px;
  }

  .form-actions,
  .detail-panel dl {
    grid-template-columns: 1fr;
  }
}
</style>
