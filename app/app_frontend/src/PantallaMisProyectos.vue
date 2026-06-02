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
</script>

<template>
  <section class="projects-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="projects-content">
      <header class="projects-header">
        <div>
          <h1>Mis proyectos</h1>
          <div class="project-stats" aria-label="Resumen de proyectos">
            <span>Todos <strong class="accent">{{ totalProjects }}</strong></span>
            <span>Pendientes <strong class="danger">{{ pendingProjects }}</strong></span>
            <span>En progreso <strong class="warning">{{ inProgressProjects }}</strong></span>
            <span>Completados <strong class="success">{{ completedProjects }}</strong></span>
          </div>
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

      <div class="project-table" role="table" aria-label="Listado de proyectos">
        <div class="project-row project-row-head" role="row">
          <span></span>
          <strong>Proyecto</strong>
          <strong>PORCENTAJE</strong>
          <strong>Colaborador</strong>
          <strong>Fecha</strong>
          <span></span>
        </div>

        <div v-for="project in orderedProjects" :key="project.id" class="project-row" role="row">
          <span class="project-check" aria-hidden="true"></span>
          <button class="project-title-button" type="button" @click="emit('view-project', project)">
            {{ project.name }}
          </button>
          <strong :class="progressClass(progress(project))">{{ progress(project) }}%</strong>
          <span class="collaborator-cell" :class="{ empty: !collaboratorsLabel(project) }">
            {{ collaboratorsLabel(project) || 'Sin colaboradores' }}
          </span>
          <time>{{ formatDate(project.end_date) }}</time>
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

.project-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  align-items: center;
  font-size: 0.88rem;
}

.project-stats strong {
  margin-left: 10px;
  font-size: 1.2rem;
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

.project-table {
  width: 100%;
  margin-top: 12px;
}

.project-row {
  min-height: 43px;
  display: grid;
  grid-template-columns: 34px minmax(240px, 1fr) minmax(130px, 0.3fr) minmax(180px, 0.42fr) minmax(120px, 0.28fr) 112px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.project-row-head {
  min-height: 28px;
}

.project-row-head strong {
  text-align: center;
  font-size: 1rem;
}

.project-row-head strong:first-of-type {
  text-align: left;
}

.project-check {
  width: 20px;
  height: 20px;
  border: 1.5px solid #00a8a8;
  border-radius: 4px;
  background: #fff;
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
}

.project-row strong,
.collaborator-cell,
.project-row time {
  text-align: center;
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
    min-width: 940px;
  }
}
</style>
