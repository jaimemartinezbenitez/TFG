<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaProyecto.vue"
Descripcion: Representa el detalle de un proyecto y sus colaboraciones.
-->

<script setup lang="ts">
import { ref } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Collaboration, Project, ShareForm, Task, UserProfile } from './types'

const props = defineProps<{
  project: Project | null
  tasks: Task[]
  initials: string
  canShare: boolean
  canEdit: boolean
  canDelete: boolean
  accessMessage: string
  shareForm: ShareForm
  shareLoading: boolean
  shareMessage: string
  collaborations: Collaboration[]
  users: UserProfile[]
}>()

const usersPopupOpen = ref(false)

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'edit-project': [project: Project]
  'delete-project': [project: Project]
  'view-task': [task: Task]
  'edit-task': [task: Task]
  'delete-task': [task: Task]
  'share-project': []
  'remove-collaboration': [collaboration: Collaboration]
}>()

function progress() {
  return props.project?.progress_percentage ?? 0
}

function projectStatus() {
  const value = progress()
  if (value === 100) return 'COMPLETADO'
  if (value > 0) return 'EN PROGRESO'
  return 'PENDIENTE'
}

function formatDate(value?: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}

function formatDateTime(value?: string) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(value))
}

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

function roleLabel(role: Collaboration['role']) {
  return {
    READER: 'Lector',
    EDITOR: 'Editor',
    ADMIN: 'Administrador',
  }[role]
}

function roleDescription(role: Collaboration['role']) {
  return {
    READER: 'puede consultar',
    EDITOR: 'puede editar y participar',
    ADMIN: 'puede editar y participar',
  }[role]
}

function collaborationStatusLabel(status: Collaboration['status']) {
  return {
    PENDING: 'pendiente de aceptar',
    ACCEPTED: 'aceptada',
    REJECTED: 'rechazada',
  }[status]
}

function selectUser(user: UserProfile) {
  props.shareForm.userIdentifier = user.email || user.username
  usersPopupOpen.value = false
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
</script>

<template>
  <section class="project-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="project-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <template v-if="props.project">
        <header class="project-heading">
          <h1>{{ props.project.name }}</h1>
          <button v-if="props.canEdit" class="detail-icon" type="button" title="Editar proyecto" @click="emit('edit-project', props.project)">
            <img src="/icono-editar.png" alt="" aria-hidden="true" />
          </button>
          <button v-if="props.canDelete" class="detail-icon" type="button" title="Eliminar proyecto" @click="emit('delete-project', props.project)">
            <img src="/icono-borrar.png" alt="" aria-hidden="true" />
          </button>
        </header>
        <p class="access-note">{{ props.accessMessage }}</p>

        <div class="project-detail-grid">
          <div class="description-block">
            <h2>Descripción</h2>
            <p>{{ props.project.description || 'Sin descripción.' }}</p>
          </div>

          <dl class="detail-fields">
            <div>
              <dt>Progreso</dt>
              <dd>{{ progress() }}%</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd><span class="dot"></span>{{ projectStatus() }}</dd>
            </div>
            <div>
              <dt>Tareas</dt>
              <dd>{{ props.project.tasks_count ?? 0 }}</dd>
            </div>
            <div>
              <dt>Proyecto</dt>
              <dd>{{ props.project.name }}</dd>
            </div>
            <div>
              <dt>Fecha de creación</dt>
              <dd>{{ formatDateTime(props.project.created_at) }}</dd>
            </div>
            <div>
              <dt>Fecha limite</dt>
              <dd>{{ formatDate(props.project.end_date) }}</dd>
            </div>
          </dl>
        </div>

        <section v-if="props.canShare" class="share-panel" aria-label="Invitar colaboradores al proyecto">
          <h2>Invitar colaboradores</h2>
          <form class="share-form" @submit.prevent="emit('share-project')">
            <label>
              Colaborador
              <span class="user-input-row">
                <input
                  v-model.trim="props.shareForm.userIdentifier"
                  type="text"
                  placeholder="usuario@correo.com"
                  autocomplete="off"
                />
                <button class="user-picker-button" type="button" @click="usersPopupOpen = true">
                  Ver usuarios
                </button>
              </span>
            </label>
            <label>
              Rol
              <select v-model="props.shareForm.role">
                <option value="READER">Lector - puede consultar</option>
                <option value="EDITOR">Editor - puede editar y participar</option>
                <option value="ADMIN">Administrador - puede editar y participar</option>
              </select>
            </label>
            <button type="submit" :disabled="props.shareLoading">
              {{ props.shareLoading ? 'Enviando invitación...' : 'Invitar a colaborar' }}
            </button>
          </form>
          <p v-if="props.shareMessage" class="share-message">{{ props.shareMessage }}</p>

          <div v-if="props.collaborations.length" class="collaborator-list">
            <strong>Colaboradores invitados</strong>
            <ul>
              <li v-for="collaboration in props.collaborations" :key="collaboration.id">
                <span>{{ collaboration.user_detail?.username || collaboration.user }}</span>
                <small>{{ roleLabel(collaboration.role) }} · {{ roleDescription(collaboration.role) }} · {{ collaborationStatusLabel(collaboration.status) }}</small>
                <button class="remove-collaborator-button" type="button" @click="emit('remove-collaboration', collaboration)">
                  Eliminar
                </button>
              </li>
            </ul>
          </div>
        </section>

        <div v-if="usersPopupOpen" class="popup-overlay" role="presentation" @click.self="usersPopupOpen = false">
          <section class="users-popup" role="dialog" aria-modal="true" aria-label="Seleccionar colaborador">
            <header>
              <h2>Seleccionar colaborador</h2>
              <button type="button" aria-label="Cerrar" @click="usersPopupOpen = false">×</button>
            </header>
            <div class="users-list">
              <button
                v-for="user in props.users"
                :key="user.id"
                type="button"
                class="user-option"
                @click="selectUser(user)"
              >
                <strong>{{ user.username }}</strong>
                <span>{{ user.email }}</span>
              </button>
              <p v-if="!props.users.length" class="empty-state">No hay otros usuarios registrados.</p>
            </div>
          </section>
        </div>

        <section class="project-tasks">
          <h2>Tareas del proyecto</h2>
          <div class="task-table" role="table" aria-label="Tareas del proyecto">
            <div class="task-row task-row-head" role="row">
              <span></span>
              <strong>Tarea</strong>
              <strong>PRIORIDAD</strong>
              <strong>ESTADO</strong>
              <strong>Creada por</strong>
              <strong>Desarrollada por</strong>
              <strong>Fecha</strong>
              <span></span>
            </div>

            <div v-for="task in props.tasks" :key="task.id" class="task-row" role="row">
              <span class="task-check" aria-hidden="true"></span>
              <button class="task-title-button" type="button" @click="emit('view-task', task)">
                {{ task.title }}
              </button>
              <strong class="priority" :class="priorityClass(task.priority)">{{ priorityLabel(task.priority) }}</strong>
              <strong class="task-status" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</strong>
              <span class="author-cell">{{ createdByLabel(task) }}</span>
              <span class="author-cell">{{ developedByLabel(task) }}</span>
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
          </div>
        </section>
      </template>

      <p v-else class="empty-state">No se ha encontrado el proyecto.</p>
    </section>
  </section>
</template>

<style scoped>
.project-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.project-content {
  position: relative;
  min-width: 0;
  padding: 76px 24px 74px 34px;
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

.project-heading {
  width: calc(100% - 80px);
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-heading h1 {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

.detail-icon,
.icon-button {
  display: grid;
  place-items: center;
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.detail-icon {
  width: 42px;
  aspect-ratio: 1;
  flex: 0 0 auto;
}

.detail-icon img {
  width: 38px;
  height: 38px;
  display: block;
  object-fit: contain;
}

.access-note {
  width: min(760px, calc(100% - 80px));
  margin: 6px 0 0;
  border-left: 4px solid #715cff;
  padding: 8px 12px;
  color: #33384a;
  background: #f6f4ff;
  font-weight: 700;
}

.project-detail-grid {
  width: 100%;
  margin-top: 8px;
  display: grid;
  grid-template-columns: minmax(280px, 0.85fr) minmax(480px, 1.35fr);
  gap: 50px;
  align-items: start;
}

.description-block h2,
.project-tasks h2 {
  margin: 0 0 6px;
  font-size: 1.35rem;
}

.description-block h2 {
  font-size: 1.1rem;
  font-weight: 500;
}

.description-block p {
  width: 100%;
  min-height: 140px;
  margin: 0;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 10px;
  overflow-wrap: anywhere;
}

.detail-fields {
  display: grid;
  grid-template-columns: repeat(3, minmax(140px, 1fr));
  gap: 20px 16px;
  margin: 23px 0 0;
}

.detail-fields div {
  min-width: 0;
  display: grid;
  grid-template-rows: auto 32px;
}

.detail-fields dt {
  margin-bottom: 6px;
  font-size: 1.05rem;
}

.detail-fields dd {
  width: 100%;
  min-width: 0;
  min-height: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  border: 2px solid #7161ff;
  padding: 3px 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dot {
  width: 20px;
  aspect-ratio: 1;
  flex: 0 0 auto;
  border-radius: 50%;
  background: #e98383;
}

.share-panel {
  width: min(940px, 100%);
  margin-top: 12px;
}

.share-panel h2 {
  margin: 0 0 12px;
  font-size: 1.25rem;
}

.share-form {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(220px, 260px) minmax(180px, auto);
  column-gap: 30px;
  row-gap: 12px;
  align-items: end;
}

.share-form label {
  display: grid;
  gap: 6px;
  font-size: 0.92rem;
}

.user-input-row {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) auto;
  gap: 8px;
}

.share-form input,
.share-form select {
  height: 34px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 4px 10px;
  background: #fff;
}

.share-form select {
  min-width: 220px;
}

.user-picker-button,
.share-form button {
  height: 34px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.share-form button {
  min-width: 180px;
  padding: 0 18px;
  white-space: nowrap;
}

.user-picker-button {
  border: 2px solid #7161ff;
  color: #715cff;
  background: #fff;
}

.share-form button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.share-message {
  margin: 10px 0 0;
  color: #555967;
}

.collaborator-list {
  margin-top: 14px;
}

.collaborator-list strong {
  display: block;
  margin-bottom: 8px;
}

.collaborator-list ul {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.collaborator-list li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #75ddcb;
  padding: 6px 0;
}

.collaborator-list small {
  color: #715cff;
  font-weight: 700;
}

.remove-collaborator-button {
  min-width: 82px;
  height: 28px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #ff2d3b;
  cursor: pointer;
}

.popup-overlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  background: rgb(0 0 0 / 30%);
}

.users-popup {
  width: min(520px, calc(100vw - 32px));
  max-height: min(560px, calc(100vh - 48px));
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 18px;
  padding: 20px;
  background: #fff;
}

.users-popup header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.users-popup h2 {
  margin: 0;
}

.users-popup header button {
  width: 34px;
  aspect-ratio: 1;
  border: 0;
  border-radius: 50%;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.users-list {
  min-height: 0;
  margin-top: 10px;
  overflow: auto;
}

.user-option {
  width: 100%;
  display: grid;
  gap: 3px;
  border: 0;
  border-bottom: 1px solid #75ddcb;
  padding: 10px 4px;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.user-option strong {
  color: #0d1430;
}

.user-option span {
  color: #715cff;
  font-size: 0.9rem;
}

.project-tasks {
  width: 100%;
  margin-top: 10px;
}

.task-table {
  width: 100%;
}

.task-row {
  min-height: 41px;
  display: grid;
  grid-template-columns: 34px minmax(220px, 1.1fr) minmax(110px, 0.28fr) minmax(140px, 0.34fr) minmax(120px, 0.3fr) minmax(160px, 0.38fr) minmax(110px, 0.28fr) 112px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.task-row-head {
  min-height: 28px;
}

.task-row-head strong {
  text-align: center;
  font-size: 1rem;
}

.task-row-head strong:first-of-type {
  text-align: left;
}

.task-check {
  width: 20px;
  height: 20px;
  border: 1.5px solid #00a8a8;
  border-radius: 4px;
  background: #fff;
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
.author-cell,
.task-row time {
  text-align: center;
}

.author-cell {
  min-width: 0;
  overflow: hidden;
  color: #715cff;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.low {
  color: #ff2d3b;
}

.medium {
  color: #ffd43b;
}

.high {
  color: #00bf63;
}

.row-actions {
  display: flex;
  justify-content: end;
  gap: 8px;
}

.icon-button {
  width: 38px;
  aspect-ratio: 1;
}

.icon-button img {
  width: 34px;
  height: 34px;
  display: block;
  object-fit: contain;
}

.empty-state {
  color: #6d7180;
}

@media (max-width: 1100px) {
  .project-detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .project-frame {
    grid-template-columns: 1fr;
  }

  .project-content {
    padding: 82px 20px 74px;
  }

  .project-heading {
    width: 100%;
  }

  .detail-fields,
  .share-form {
    grid-template-columns: 1fr;
  }

  .task-table {
    overflow-x: auto;
  }

  .task-row {
    min-width: 1180px;
  }
}
</style>
