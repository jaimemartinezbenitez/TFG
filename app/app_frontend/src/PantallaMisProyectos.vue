<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaMisProyectos.vue"
Descripcion: Representa el listado general de proyectos del usuario.
-->

<script setup lang="ts">
import { computed, ref } from 'vue'
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

const searchText = ref('')
const progressFilter = ref<'ALL' | 'PENDING' | 'IN_PROGRESS' | 'COMPLETED'>('ALL')
const accessFilter = ref<'ALL' | 'OWN' | 'SHARED'>('ALL')
const collaboratorFilter = ref<'ALL' | 'WITH' | 'WITHOUT'>('ALL')
const dateFilter = ref<'ALL' | 'ACTIVE' | 'ENDING_SOON' | 'FINISHED' | 'NO_DATE'>('ALL')
const sortMode = ref<'END_DATE' | 'PROGRESS' | 'CREATED_AT' | 'NAME' | 'TASKS'>('END_DATE')

const todayIso = computed(() => new Date().toISOString().slice(0, 10))

const visibleProjects = computed(() => {
  const search = searchText.value.trim().toLowerCase()
  const today = todayIso.value
  const weekLimit = new Date()
  weekLimit.setDate(weekLimit.getDate() + 7)
  const weekLimitIso = weekLimit.toISOString().slice(0, 10)

  return props.projects.filter((project) => {
    const projectProgress = progress(project)
    const collaborators = project.collaborators || []

    if (search) {
      const searchable = [
        project.name,
        project.description,
        project.owner?.username,
        ...collaborators.map((collaborator) => collaborator.username),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      if (!searchable.includes(search)) return false
    }

    if (progressFilter.value === 'PENDING' && projectProgress > 0) return false
    if (progressFilter.value === 'IN_PROGRESS' && (projectProgress <= 0 || projectProgress >= 100)) return false
    if (progressFilter.value === 'COMPLETED' && projectProgress < 100) return false

    if (accessFilter.value === 'OWN' && !project.is_owner) return false
    if (accessFilter.value === 'SHARED' && !project.collaboration_role) return false

    if (collaboratorFilter.value === 'WITH' && !collaborators.length) return false
    if (collaboratorFilter.value === 'WITHOUT' && collaborators.length) return false

    if (dateFilter.value === 'ACTIVE') {
      if ((project.start_date && project.start_date > today) || (project.end_date && project.end_date < today)) return false
    }
    if (dateFilter.value === 'ENDING_SOON' && (!project.end_date || project.end_date < today || project.end_date > weekLimitIso)) return false
    if (dateFilter.value === 'FINISHED' && (!project.end_date || project.end_date >= today)) return false
    if (dateFilter.value === 'NO_DATE' && (project.start_date || project.end_date)) return false

    return true
  })
})

const orderedProjects = computed(() =>
  [...visibleProjects.value].sort((a, b) => {
    if (sortMode.value === 'PROGRESS') {
      return progress(b) - progress(a) || a.name.localeCompare(b.name)
    }
    if (sortMode.value === 'CREATED_AT') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
    if (sortMode.value === 'NAME') {
      return a.name.localeCompare(b.name)
    }
    if (sortMode.value === 'TASKS') {
      return (b.tasks_count || 0) - (a.tasks_count || 0) || a.name.localeCompare(b.name)
    }
    const first = a.end_date || '9999-12-31'
    const second = b.end_date || '9999-12-31'
    return first.localeCompare(second) || a.name.localeCompare(b.name)
  }),
)

const activeFilters = computed(() =>
  Boolean(
    searchText.value.trim() ||
      progressFilter.value !== 'ALL' ||
      accessFilter.value !== 'ALL' ||
      collaboratorFilter.value !== 'ALL' ||
      dateFilter.value !== 'ALL' ||
      sortMode.value !== 'END_DATE',
  ),
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
const filteredCount = computed(() => orderedProjects.value.length)

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
  if (project.collaboration_role) return `Compartido · ${roleLabel(project.collaboration_role)}`
  return 'Proyecto'
}

function roleLabel(role: Project['collaboration_role']) {
  return {
    OWNER: 'Propietario',
    READER: 'Lector',
    EDITOR: 'Editor',
    ADMIN: 'Administrador',
  }[role || 'READER']
}

function clearFilters() {
  searchText.value = ''
  progressFilter.value = 'ALL'
  accessFilter.value = 'ALL'
  collaboratorFilter.value = 'ALL'
  dateFilter.value = 'ALL'
  sortMode.value = 'END_DATE'
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

      <section class="project-filters" aria-label="Filtros de proyectos">
        <label class="search-field">
          Buscar proyecto
          <input v-model.trim="searchText" type="search" placeholder="Nombre, descripción o colaborador" />
        </label>

        <label>
          Progreso
          <select v-model="progressFilter">
            <option value="ALL">Todos</option>
            <option value="PENDING">Pendientes</option>
            <option value="IN_PROGRESS">En progreso</option>
            <option value="COMPLETED">Completados</option>
          </select>
        </label>

        <label>
          Acceso
          <select v-model="accessFilter">
            <option value="ALL">Todos</option>
            <option value="OWN">Propios</option>
            <option value="SHARED">Compartidos</option>
          </select>
        </label>

        <label>
          Colaboradores
          <select v-model="collaboratorFilter">
            <option value="ALL">Todos</option>
            <option value="WITH">Con colaboradores</option>
            <option value="WITHOUT">Sin colaboradores</option>
          </select>
        </label>

        <label>
          Fecha
          <select v-model="dateFilter">
            <option value="ALL">Todas</option>
            <option value="ACTIVE">Activos ahora</option>
            <option value="ENDING_SOON">Finalizan pronto</option>
            <option value="FINISHED">Finalizados</option>
            <option value="NO_DATE">Sin fechas</option>
          </select>
        </label>

        <label>
          Ordenar por
          <select v-model="sortMode">
            <option value="END_DATE">Fecha final</option>
            <option value="PROGRESS">Progreso</option>
            <option value="CREATED_AT">Más recientes</option>
            <option value="NAME">Nombre</option>
            <option value="TASKS">Número de tareas</option>
          </select>
        </label>

        <button class="clear-filter-button" type="button" :disabled="!activeFilters" @click="clearFilters">
          Limpiar filtros
        </button>
      </section>

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
        <article>
          <span>Mostrados</span>
          <strong class="accent">{{ filteredCount }}</strong>
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
            <button class="text-action" type="button" @click="emit('view-project', project)">
              Ver
            </button>
            <button v-if="project.can_edit" class="text-action primary" type="button" @click="emit('edit-project', project)">
              Editar
            </button>
            <button v-if="project.is_owner" class="text-action danger-action" type="button" @click="emit('delete-project', project)">
              Eliminar
            </button>
          </div>
        </div>

        <p v-if="!props.loading && !orderedProjects.length" class="empty-state">
          {{ totalProjects ? 'No hay proyectos que coincidan con los filtros.' : 'Aún no tienes proyectos.' }}
        </p>
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
  padding: 32px 12px 50px 16px;
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
  width: min(100%, 1180px);
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(138px, 1fr));
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
  gap: 12px;
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

.project-filters {
  width: min(100%, 1180px);
  margin-top: 20px;
  display: grid;
  grid-template-columns: minmax(190px, 1.3fr) repeat(3, minmax(120px, 0.9fr));
  gap: 8px;
  align-items: end;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fbfffe;
  padding: 10px;
}

.project-filters label {
  min-width: 0;
  display: grid;
  gap: 6px;
  color: #565b6a;
  font-size: 0.82rem;
  font-weight: 800;
}

.project-filters input,
.project-filters select {
  width: 100%;
  min-height: 32px;
  border: 1.5px solid #75ddcb;
  border-radius: 6px;
  background: #fff;
  color: #171a22;
  padding: 0 8px;
  font: inherit;
  font-weight: 600;
  font-size: 0.9rem;
}

.search-field {
  grid-column: span 1;
}

.clear-filter-button {
  min-height: 32px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  padding: 0 12px;
  font-weight: 800;
  cursor: pointer;
  white-space: nowrap;
  font-size: 0.85rem;
}

.clear-filter-button:disabled {
  opacity: 0.45;
  cursor: default;
}

.project-table-shell {
  width: min(100%, 1180px);
  margin-top: 20px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fff;
  overflow-x: auto;
  overflow-y: hidden;
}

.project-table {
  width: 100%;
  min-width: 980px;
}

.project-row {
  min-height: 80px;
  display: grid;
  grid-template-columns: 24px minmax(250px, 1fr) minmax(130px, 0.35fr) 70px minmax(150px, 0.3fr) 200px;
  gap: 8px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
  padding: 0 10px;
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
  flex-wrap: wrap;
  justify-content: end;
  gap: 6px;
}

.text-action {
  min-height: 26px;
  border: 1.5px solid #d5f6ef;
  border-radius: 999px;
  background: #fff;
  color: #34384a;
  padding: 0 8px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  font-size: 0.75rem;
}

.text-action.primary {
  border-color: #715cff;
  color: #715cff;
}

.danger-action {
  border-color: #ffb7bf;
  color: #d91f2d;
}

@media (max-width: 860px) {
  .projects-frame {
    grid-template-columns: 1fr;
  }

  .projects-content {
    padding: 16px 8px 40px 8px;
  }

  .projects-header {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .header-actions {
    justify-items: start;
    gap: 8px;
  }

  .project-filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding: 8px;
  }

  .project-row {
    min-height: 70px;
  }

  .project-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .projects-frame {
    margin: 1px;
    grid-template-columns: 1fr;
    border-radius: 12px;
  }

  .projects-content {
    padding: 12px 6px 30px 6px;
  }

  .projects-header h1 {
    font-size: clamp(1.8rem, 4vw, 2.5rem);
  }

  .projects-header p {
    font-size: 0.9rem;
  }

  .project-filters {
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 6px;
  }

  .project-filters label {
    font-size: 0.75rem;
  }

  .project-filters input,
  .project-filters select {
    min-height: 28px;
    padding: 0 6px;
    font-size: 0.8rem;
  }

  .clear-filter-button {
    min-height: 28px;
    padding: 0 8px;
    font-size: 0.75rem;
  }

  .project-stats {
    gap: 8px;
  }

  .project-stats article {
    min-height: 60px;
    padding: 8px 10px;
  }

  .project-stats strong {
    font-size: 1.2rem;
  }

  .project-row {
    grid-template-columns: 16px minmax(60px, 1fr) minmax(60px, 0.25fr) 50px minmax(60px, 0.25fr) 60px;
    gap: 4px;
    padding: 0 6px;
    min-height: 75px;
  }

  .project-title-button {
    font-size: 0.85rem;
  }

  .project-main-cell small {
    font-size: 0.7rem;
  }

  .project-meta span {
    max-width: 100px;
    font-size: 0.7rem;
  }

  .progress-cell strong,
  .tasks-count,
  .project-row time {
    font-size: 0.75rem;
  }

  .progress-cell {
    gap: 4px;
  }

  .progress-track {
    height: 6px;
  }

  .icon-button {
    width: 24px;
  }

  .icon-button img {
    width: 18px;
    height: 18px;
  }
}
</style>
