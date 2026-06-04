<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaMisProyectos.vue"
Descripcion: Representa el listado general de proyectos del usuario.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Project } from './types'

const props = defineProps<{
  projects: Project[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'create-project': []
  'view-project': [project: Project]
  'edit-project': [project: Project]
  'delete-project': [project: Project]
}>()

const orderedProjects = computed(() =>
  [...props.projects].sort((a, b) => {
    const first = a.end_date || '9999-12-31'
    const second = b.end_date || '9999-12-31'
    return first.localeCompare(second) || a.name.localeCompare(b.name)
  }),
)

const totalProjects = computed(() => props.projects.length)
const pendingProjects = computed(() => props.projects.filter((project) => progress(project) <= 0).length)
const inProgressProjects = computed(() =>
  props.projects.filter((project) => {
    const value = progress(project)
    return value > 0 && value < 100
  }).length,
)
const completedProjects = computed(() => props.projects.filter((project) => progress(project) >= 100).length)
const totalProjectTasks = computed(() =>
  props.projects.reduce((total, project) => total + (project.tasks_count || 0), 0),
)

function progress(project: Project) {
  return project.progress_percentage ?? 0
}

function progressClass(value: number) {
  if (value >= 70) return 'success'
  if (value >= 40) return 'accent'
  return 'danger'
}

function formatDate(value: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}

function collaboratorsLabel(project: Project) {
  const collaborators = project.collaborators || []
  if (!collaborators.length) return ''
  const names = collaborators.map((collaborator) => collaborator.username)
  if (names.length <= 2) return names.join(', ')
  return `${names.slice(0, 2).join(', ')} +${names.length - 2}`
}

function dateRange(project: Project) {
  return `${formatDate(project.start_date)} · ${formatDate(project.end_date)}`
}

function accessLabel(project: Project) {
  if (project.is_owner) return 'Propio'
  if (project.collaboration_role) return `Compartido · ${project.collaboration_role}`
  return 'Proyecto'
}
</script>

<template>
  <section class="projects-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="projects-content">
      <header class="projects-header">
        <div>
          <h1>Mis proyectos</h1>
          <p>Controla el avance, las fechas y los colaboradores.</p>
        </div>
        <div class="header-actions">
          <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
            <span>{{ props.initials }}</span>
          </button>
          <button class="new-project-button" type="button" @click="emit('create-project')">
            <span aria-hidden="true">+</span>
            Nuevo proyecto
          </button>
        </div>
      </header>

      <p v-if="props.message" class="project-message">{{ props.message }}</p>
      <p v-else-if="props.loading" class="project-message">Cargando proyectos...</p>

      <div class="project-stats" aria-label="Resumen de proyectos">
        <article>
          <span>Total</span>
          <strong class="accent">{{ totalProjects }}</strong>
        </article>
        <article>
          <span>Pendientes</span>
          <strong class="danger">{{ pendingProjects }}</strong>
        </article>
        <article>
          <span>En progreso</span>
          <strong class="warning">{{ inProgressProjects }}</strong>
        </article>
        <article>
          <span>Completados</span>
          <strong class="success">{{ completedProjects }}</strong>
        </article>
        <article>
          <span>Tareas</span>
          <strong class="accent">{{ totalProjectTasks }}</strong>
        </article>
      </div>

      <div class="project-table-shell">
      <div class="project-table" role="table" aria-label="Listado de proyectos">
        <div class="project-row project-row-head" role="row">
          <span></span>
          <strong>Proyecto</strong>
          <strong>Progreso</strong>
          <strong>Tareas</strong>
          <strong>Fechas</strong>
          <span></span>
        </div>

        <div v-for="project in orderedProjects" :key="project.id" class="project-row" role="row">
          <span class="project-state-dot" :class="progressClass(progress(project))" aria-hidden="true"></span>
          <div class="project-main-cell">
            <button class="project-title-button" type="button" @click="emit('view-project', project)">
              {{ project.name }}
            </button>
            <small>{{ project.description || 'Sin descripcion' }}</small>
            <div class="project-meta">
              <span>{{ accessLabel(project) }}</span>
              <span>{{ collaboratorsLabel(project) || 'Sin colaboradores' }}</span>
            </div>
          </div>
          <div class="progress-cell">
            <strong :class="progressClass(progress(project))">{{ progress(project) }}%</strong>
            <span class="progress-track">
              <span class="progress-fill" :class="progressClass(progress(project))" :style="{ width: `${progress(project)}%` }"></span>
            </span>
          </div>
          <span class="tasks-count">{{ project.completed_tasks_count || 0 }} / {{ project.tasks_count || 0 }}</span>
          <time>{{ dateRange(project) }}</time>
          <div class="row-actions">
            <button v-if="project.can_edit" class="icon-button" type="button" title="Editar proyecto" @click="emit('edit-project', project)">
              <img src="/icono-editar.png" alt="" aria-hidden="true" />
            </button>
            <button v-if="project.is_owner" class="icon-button" type="button" title="Eliminar proyecto" @click="emit('delete-project', project)">
              <img src="/icono-borrar.png" alt="" aria-hidden="true" />
            </button>
          </div>
        </div>

        <p v-if="!props.loading && !orderedProjects.length" class="empty-state">Aun no tienes proyectos.</p>
      </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.projects-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.projects-content {
  min-width: 0;
  padding: 62px 24px 74px 52px;
}

.projects-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: start;
}

.projects-header h1 {
  margin: 0 0 8px;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

.projects-header p {
  margin: 0;
  color: #6d7180;
  font-size: 1.04rem;
}

.project-stats {
  width: min(100%, 980px);
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(5, minmax(118px, 1fr));
  gap: 12px;
}

.project-stats article {
  min-height: 78px;
  display: grid;
  align-content: center;
  gap: 6px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fbfffe;
  padding: 12px 14px;
}

.project-stats span {
  color: #6d7180;
  font-size: 0.82rem;
}

.project-stats strong {
  font-size: 1.55rem;
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

.new-project-button {
  min-width: 156px;
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

.new-project-button span {
  font-weight: 800;
}

.project-message,
.empty-state {
  color: #6d7180;
}

.project-message {
  margin: 18px 0 0;
}

.project-table-shell {
  width: min(100%, 1180px);
  margin-top: 22px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.project-table {
  width: 100%;
}

.project-row {
  min-height: 86px;
  display: grid;
  grid-template-columns: 34px minmax(300px, 1fr) minmax(170px, 0.35fr) 100px minmax(170px, 0.35fr) 104px;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
  padding: 0 18px;
}

.project-row-head {
  min-height: 42px;
  background: #fbfffe;
}

.project-row-head strong {
  color: #565b6a;
  text-align: left;
  font-size: 0.82rem;
  text-transform: uppercase;
}

.project-row-head strong:nth-of-type(n + 2) {
  text-align: center;
}

.project-state-dot {
  width: 16px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: currentColor;
}

.project-title-button {
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

.project-main-cell {
  min-width: 0;
  display: grid;
  gap: 5px;
}

.project-main-cell small {
  min-width: 0;
  overflow: hidden;
  color: #8d91a1;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.78rem;
}

.project-meta {
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.project-meta span {
  max-width: 220px;
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

.progress-cell {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.progress-cell strong,
.tasks-count,
.project-row time {
  text-align: center;
}

.progress-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #eef1f6;
}

.progress-fill {
  height: 100%;
  display: block;
  border-radius: inherit;
  background: currentColor;
}

.accent {
  color: #715cff;
}

.danger {
  color: #ff2d3b;
}

.warning {
  color: #ffd43b;
}

.success {
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
  .projects-frame {
    grid-template-columns: 1fr;
  }

  .projects-content {
    padding: 28px 16px 74px;
  }

  .projects-header {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-items: start;
    gap: 16px;
  }

  .project-table {
    overflow-x: auto;
  }

  .project-row {
    min-width: 900px;
  }

  .project-stats {
    grid-template-columns: 1fr;
  }
}
</style>
