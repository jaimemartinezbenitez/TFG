<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaCrearProyecto.vue"
Descripcion: Representa el formulario para crear proyectos.
-->

<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
import type { CollaboratorRole, ProjectForm, UserProfile } from './types'

const props = defineProps<{
  form: ProjectForm
  users: UserProfile[]
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

function roleLabel(role: CollaboratorRole) {
  if (role === 'ADMIN') return 'Administrador'
  if (role === 'EDITOR') return 'Editor'
  return 'Lector'
}
</script>

<template>
  <section class="project-form-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="project-form-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>{{ props.mode === 'create' ? 'Crear proyecto' : 'Editar proyecto' }}</h1>
      <h2>{{ props.mode === 'create' ? 'Nuevo proyecto' : props.form.name || 'Proyecto' }}</h2>

      <form class="project-form" @submit.prevent="emit('submit')">
        <section class="form-section main-fields" aria-label="Datos principales del proyecto">
          <div class="section-title">
            <span>01</span>
            <strong>Datos del proyecto</strong>
          </div>

          <label for="projectName">Título</label>
          <input id="projectName" v-model.trim="props.form.name" required maxlength="80" placeholder="Nombre del proyecto" />

          <label for="projectDescription">Descripción</label>
          <textarea id="projectDescription" v-model.trim="props.form.description" placeholder="Describe el proyecto..."></textarea>
        </section>

        <section class="form-section date-fields" aria-label="Fechas del proyecto">
          <div class="section-title">
            <span>02</span>
            <strong>Fechas</strong>
          </div>

          <label for="projectStart">Fecha inicio</label>
          <input id="projectStart" v-model="props.form.start_date" type="date" />

          <label for="projectEnd">Fecha finalización</label>
          <input id="projectEnd" v-model="props.form.end_date" type="date" />
        </section>

        <section v-if="props.mode === 'create'" class="form-section collaboration-fields" aria-label="Colaboración del proyecto">
          <div class="section-title">
            <span>03</span>
            <strong>Colaboración</strong>
          </div>

          <label for="projectCollaborator">Colaborador</label>
          <input
            id="projectCollaborator"
            v-model.trim="props.form.collaboratorIdentifier"
            list="projectCollaboratorUsers"
            placeholder="Usuario o correo"
          />
          <datalist id="projectCollaboratorUsers">
            <option v-for="user in props.users" :key="user.id" :value="user.email">
              {{ user.username }}
            </option>
          </datalist>

          <label for="projectCollaboratorRole">Rol</label>
          <select id="projectCollaboratorRole" v-model="props.form.collaboratorRole">
            <option value="READER">{{ roleLabel('READER') }}</option>
            <option value="EDITOR">{{ roleLabel('EDITOR') }}</option>
            <option value="ADMIN">{{ roleLabel('ADMIN') }}</option>
          </select>
        </section>

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
.project-form-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.project-form-content {
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

.project-form {
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

.date-fields,
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
  font-size: 0.9rem;
  font-weight: 700;
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
  height: 28px;
  padding: 0 6px;
  font-size: 0.9rem;
}

textarea {
  min-height: 100px;
  resize: vertical;
  padding: 6px;
  font-size: 0.9rem;
}

input::placeholder,
textarea::placeholder {
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
  grid-template-columns: 130px 160px;
  justify-content: center;
  gap: 16px;
  margin-top: 6px;
}

.cancel-button,
.save-button {
  height: 30px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 700;
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
  .project-form {
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
  .project-form-frame {
    grid-template-columns: 1fr;
  }

  .project-form-content {
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
  .project-form-frame {
    margin: 1px;
    border-radius: 12px;
  }

  .project-form-content {
    padding: 12px 6px 30px 6px;
  }

  h1 {
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
  }

  .project-form {
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
