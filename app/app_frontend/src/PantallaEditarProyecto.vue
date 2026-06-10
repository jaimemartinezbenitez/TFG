<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaEditarProyecto.vue"
Descripcion: Representa el formulario para editar proyectos.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Project, ProjectForm, Task } from './types'

const props = defineProps<{
  project: Project | null
  tasks: Task[]
  form: ProjectForm
  initials: string
  loading: boolean
  message: string
  mode: 'create' | 'edit'
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  submit: []
  cancel: []
}>()

const progress = computed(() => props.project?.progress_percentage ?? 0)
const projectTasks = computed(() => props.tasks)
const completedTasks = computed(() => props.tasks.filter((task) => task.status === 'COMPLETED').length)
const pendingTasks = computed(() => props.tasks.filter((task) => task.status !== 'COMPLETED' && task.status !== 'CANCELLED').length)

const collaboratorsLabel = computed(() => {
  const collaborators = props.project?.collaborators || []
  if (!collaborators.length) return 'Sin colaboradores'
  return collaborators.map((collaborator) => `${collaborator.username} (${roleLabel(collaborator.role)})`).join(', ')
})

function projectStatus() {
  if (progress.value === 100) return 'COMPLETADO'
  if (progress.value > 0) return 'EN PROGRESO'
  return 'PENDIENTE'
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
  <section class="project-edit-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="project-edit-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <header class="edit-header">
        <div>
          <h1>Editar proyecto</h1>
          <p>{{ props.project?.name || props.form.name || 'Proyecto seleccionado' }}</p>
        </div>
      </header>

      <form class="edit-layout" @submit.prevent="emit('submit')">
        <section class="edit-panel" aria-label="Campos editables del proyecto">
          <h2>Datos editables</h2>
          <div class="form-grid">
            <label class="wide" for="projectName">
              Nombre
              <input id="projectName" v-model.trim="props.form.name" required maxlength="80" placeholder="Nombre del proyecto" />
            </label>

            <label class="wide" for="projectDescription">
              Descripción
              <textarea id="projectDescription" v-model.trim="props.form.description" placeholder="Describe el proyecto..."></textarea>
            </label>

            <label for="projectStart">
              Fecha inicio
              <input id="projectStart" v-model="props.form.start_date" type="date" />
            </label>

            <label for="projectEnd">
              Fecha finalización
              <input id="projectEnd" v-model="props.form.end_date" type="date" />
            </label>
          </div>
        </section>

        <aside class="detail-panel" aria-label="Información actual del proyecto">
          <h2>Información del proyecto</h2>
          <dl>
            <div>
              <dt>Propietario</dt>
              <dd>{{ props.project?.owner?.username || 'Sin usuario' }}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{{ projectStatus() }}</dd>
            </div>
            <div>
              <dt>Progreso</dt>
              <dd>{{ progress }}%</dd>
            </div>
            <div>
              <dt>Tareas</dt>
              <dd>{{ projectTasks.length }}</dd>
            </div>
            <div>
              <dt>Completadas</dt>
              <dd>{{ completedTasks }}</dd>
            </div>
            <div>
              <dt>Pendientes</dt>
              <dd>{{ pendingTasks }}</dd>
            </div>
            <div>
              <dt>Colaboradores</dt>
              <dd>{{ collaboratorsLabel }}</dd>
            </div>
            <div>
              <dt>Fecha de creación</dt>
              <dd>{{ formatDateTime(props.project?.created_at) }}</dd>
            </div>
            <div>
              <dt>Última actualización</dt>
              <dd>{{ formatDateTime(props.project?.updated_at) }}</dd>
            </div>
            <div>
              <dt>Fecha inicio</dt>
              <dd>{{ formatDate(props.form.start_date || props.project?.start_date) }}</dd>
            </div>
            <div>
              <dt>Fecha finalización</dt>
              <dd>{{ formatDate(props.form.end_date || props.project?.end_date) }}</dd>
            </div>
          </dl>
        </aside>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <div class="form-actions">
          <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">Cancelar</button>
          <button class="save-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Guardando...' : 'Guardar proyecto' }}
          </button>
        </div>
      </form>
    </section>
  </section>
</template>

<style scoped>
.project-edit-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.project-edit-content {
  position: relative;
  min-width: 0;
  padding: 62px 28px 74px;
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
  width: min(100%, 1180px);
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
  width: min(100%, 1180px);
  margin-top: 10px;
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(300px, 0.75fr);
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
textarea {
  width: 100%;
  border: 2px solid #7161ff;
  border-radius: 8px;
  background: #fff;
  outline: none;
}

input {
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

@media (max-width: 900px) {
  .edit-layout {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .form-actions {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

@media (max-width: 860px) {
  .project-edit-frame {
    grid-template-columns: 1fr;
  }

  .project-edit-content {
    padding: 82px 20px 74px;
  }

  .edit-header h1 {
    font-size: clamp(1.5rem, 3vw, 2rem);
  }

  .edit-header p {
    font-size: 0.9rem;
  }

  .form-actions,
  .detail-panel dl {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .project-edit-frame {
    margin: 1px;
    border-radius: 12px;
  }

  .project-edit-content {
    padding: 82px 12px 40px;
  }

  .edit-header h1 {
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
  }

  .edit-header {
    width: 100%;
  }

  .edit-layout {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-top: 6px;
  }

  h2 {
    font-size: 0.95rem;
    margin-bottom: 8px;
  }

  .form-grid {
    gap: 8px;
  }

  label {
    font-size: 0.75rem;
  }

  input,
  textarea {
    border-width: 1.5px;
  }

  input,
  select {
    height: 26px;
    padding: 0 4px;
    font-size: 0.8rem;
  }

  textarea {
    min-height: 80px;
    padding: 4px;
    font-size: 0.8rem;
  }

  .form-actions {
    gap: 8px;
    margin-top: 4px;
  }

  .cancel-button,
  .save-button {
    height: 28px;
    font-size: 0.75rem;
  }

  .detail-panel {
    padding: 10px;
  }

  .detail-panel dl {
    gap: 8px;
  }

  .detail-panel dd {
    font-size: 0.8rem;
  }
}
</style>
