<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaCrearTarea.vue"
Descripcion: Representa el formulario para crear tareas.
-->

<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
import type { CollaboratorRole, Project, TaskForm, UserProfile } from './types'

const props = defineProps<{
  form: TaskForm
  projects: Project[]
  users: UserProfile[]
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

function roleLabel(role: CollaboratorRole) {
  if (role === 'ADMIN') return 'Administrador'
  if (role === 'EDITOR') return 'Editor'
  return 'Lector'
}
</script>

<template>
  <section class="task-form-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="task-form-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>Crear tarea</h1>
      <h2>Nueva tarea</h2>

      <form class="task-form" @submit.prevent="emit('submit')">
        <section class="form-section main-fields" aria-label="Datos principales de la tarea">
          <div class="section-title">
            <span>01</span>
            <strong>Datos de la tarea</strong>
          </div>

          <label for="taskTitle">Título</label>
          <input id="taskTitle" v-model.trim="props.form.title" required maxlength="50" placeholder="Nombre de la tarea" />

          <label for="taskDescription">Descripción</label>
          <textarea id="taskDescription" v-model.trim="props.form.description" placeholder="Describe la tarea..."></textarea>
        </section>

        <section class="form-section planning-fields" aria-label="Planificación de la tarea">
          <div class="section-title">
            <span>02</span>
            <strong>Planificación</strong>
          </div>

          <label for="taskDate">Fecha límite</label>
          <input id="taskDate" v-model="props.form.due_date" type="date" />

          <label for="taskPriority">Prioridad</label>
          <select id="taskPriority" v-model="props.form.priority">
            <option value="HIGH">ALTA</option>
            <option value="MEDIUM">MEDIA</option>
            <option value="LOW">BAJA</option>
          </select>

          <label for="taskProject">Proyecto</label>
          <select id="taskProject" v-model="props.form.project">
            <option value="">Seleccionar proyecto...</option>
            <option v-for="project in props.projects" :key="project.id" :value="String(project.id)">
              {{ project.name }}
            </option>
          </select>
        </section>

        <section class="form-section collaboration-fields" aria-label="Colaboración de la tarea">
          <div class="section-title">
            <span>03</span>
            <strong>Colaboración</strong>
          </div>

          <label for="taskCollaborator">Colaborador</label>
          <input
            id="taskCollaborator"
            v-model.trim="props.form.collaboratorIdentifier"
            list="taskCollaboratorUsers"
            placeholder="Usuario o correo"
          />
          <datalist id="taskCollaboratorUsers">
            <option v-for="user in props.users" :key="user.id" :value="user.email">
              {{ user.username }}
            </option>
          </datalist>

          <label for="taskCollaboratorRole">Rol</label>
          <select id="taskCollaboratorRole" v-model="props.form.collaboratorRole">
            <option value="READER">{{ roleLabel('READER') }}</option>
            <option value="EDITOR">{{ roleLabel('EDITOR') }}</option>
            <option value="ADMIN">{{ roleLabel('ADMIN') }}</option>
          </select>
        </section>

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
.task-form-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.task-form-content {
  position: relative;
  min-width: 0;
  padding: 32px 20px 50px 16px;
}

.avatar-button {
  position: absolute;
  top: 8px;
  right: 12px;
  width: 50px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 4px solid #715cff;
  border-radius: 50%;
  color: #fff;
  background:
    linear-gradient(#8794ea 0 0) center 11px / 20px 20px no-repeat,
    linear-gradient(#8794ea 0 0) center 31px / 34px 15px no-repeat,
    #f8f8ff;
  cursor: pointer;
  font-size: 0.8rem;
}

.avatar-button span {
  position: relative;
  top: -5px;
  font-weight: 800;
}

h1 {
  margin: 0 0 6px;
  font-size: clamp(2rem, 4vw, 2.8rem);
  line-height: 1;
}

h2 {
  margin: 0 0 12px;
  font-size: 1.1rem;
}

.task-form {
  max-width: 100%;
  display: grid;
  grid-template-columns: minmax(250px, 1fr) minmax(200px, 0.8fr);
  gap: 16px 20px;
}

.form-section {
  display: grid;
  align-content: start;
  gap: 8px;
  padding: 12px 14px 14px;
  border: 1.5px solid #a6f1df;
  border-radius: 6px;
  background: #fbfffe;
}

.main-fields {
  min-height: 278px;
  grid-row: span 2;
}

.planning-fields,
.collaboration-fields {
  min-height: 0;
}

.collaboration-fields {
  grid-column: 2;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2px;
}

.section-title span {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #fff;
  background: #715cff;
  font-size: 0.82rem;
  font-weight: 800;
}

.section-title strong {
  font-size: 1.08rem;
}

label {
  font-size: 1.05rem;
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
  height: 30px;
  padding: 0 8px;
}

textarea {
  min-height: 132px;
  resize: vertical;
  padding: 8px;
}

input::placeholder,
textarea::placeholder,
select:invalid {
  color: #b8bac4;
  font-style: italic;
}

select {
  cursor: pointer;
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
  margin-top: 8px;
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

@media (max-width: 900px) {
  .task-form {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .main-fields,
  .collaboration-fields {
    grid-column: auto;
    grid-row: auto;
  }

  .form-actions {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

@media (max-width: 860px) {
  .task-form-frame {
    grid-template-columns: 1fr;
  }

  .task-form-content {
    padding: 16px 8px 40px 8px;
  }

  h1 {
    font-size: clamp(1.5rem, 3vw, 2rem);
  }

  h2 {
    font-size: 0.95rem;
  }

  .avatar-button {
    top: 6px;
    right: 6px;
    width: 40px;
    border-width: 3px;
  }
}

@media (max-width: 600px) {
  .task-form-frame {
    margin: 1px;
    border-radius: 12px;
  }

  .task-form-content {
    padding: 12px 6px 30px 6px;
  }

  h1 {
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
  }

  .task-form {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .form-section {
    gap: 6px;
    padding: 10px 10px 10px;
  }

  .section-title span {
    width: 22px;
    height: 22px;
    font-size: 0.7rem;
  }

  .section-title strong {
    font-size: 0.9rem;
  }

  label {
    font-size: 0.8rem;
    font-weight: 700;
  }

  input,
  select,
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
}
</style>
