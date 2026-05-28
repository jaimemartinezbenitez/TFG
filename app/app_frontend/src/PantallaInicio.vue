<script setup lang="ts">
import type { ActivityItem, DashboardTaskItem } from './types'

const props = defineProps<{
  displayName: string
  initials: string
  pendingTasks: number
  completedTasks: number
  activeProjects: number
  effectiveMinutes: number
  upcomingTasks: DashboardTaskItem[]
  recentActivity: ActivityItem[]
  dashboardLoading: boolean
  dashboardMessage: string
}>()

const emit = defineEmits<{
  logout: []
}>()
</script>

<template>
  <section class="dashboard-frame">
    <aside class="sidebar">
      <img class="company-icon" src="/icono.png" alt="ConcentraPlus" />

      <nav class="nav-menu" aria-label="Navegacion principal">
        <button class="nav-item active" type="button"><span class="nav-icon">⌂</span>Inicio</button>
        <button class="nav-item" type="button"><span class="nav-icon">☑</span>Tareas</button>
        <button class="nav-item" type="button"><span class="nav-icon">▦</span>Proyecto</button>
        <button class="nav-item" type="button"><span class="nav-icon">□</span>Calendario</button>
        <button class="nav-item" type="button"><span class="nav-icon">✣</span>Tecnicas</button>
        <button class="nav-item" type="button"><span class="nav-icon">▥</span>Estadisticas</button>
        <button class="nav-item" type="button"><span class="nav-icon">☆</span>Logros</button>
        <button class="nav-item" type="button"><span class="nav-icon">⚙</span>Exportar datos</button>
      </nav>
    </aside>

    <section class="dashboard-content">
      <header class="dashboard-header">
        <div>
          <h1>¡Hola, {{ props.displayName }}!</h1>
          <p>Aqui tienes un resumen de tu productividad</p>
        </div>
        <button class="avatar-button" type="button" title="Cerrar sesion" @click="emit('logout')">
          <span>{{ props.initials }}</span>
        </button>
      </header>

      <p v-if="props.dashboardMessage" class="dashboard-error">{{ props.dashboardMessage }}</p>
      <p v-else-if="props.dashboardLoading" class="loading-copy">Cargando resumen...</p>

      <div class="stats-row" aria-label="Resumen de productividad">
        <article>
          <span>Tareas pendientes</span>
          <strong class="danger">{{ props.pendingTasks }}</strong>
        </article>
        <article>
          <span>Tareas completadas</span>
          <strong class="accent">{{ props.completedTasks }}</strong>
        </article>
        <article>
          <span>Proyectos activos</span>
          <strong>{{ props.activeProjects }}</strong>
        </article>
        <article>
          <span>Minutos efectivos</span>
          <strong>{{ props.effectiveMinutes }}</strong>
        </article>
      </div>

      <div class="dashboard-grid">
        <section class="panel">
          <h2>Tareas proximas:</h2>
          <ul class="task-list">
            <li v-for="task in props.upcomingTasks" :key="task.id">
              <span class="alert-icon">!</span>
              <span class="task-title">{{ task.title }}</span>
              <time>{{ task.dateLabel }}</time>
            </li>
            <li v-if="!props.upcomingTasks.length" class="empty-row">No hay tareas proximas.</li>
          </ul>
        </section>

        <section class="panel">
          <h2>Actividad reciente:</h2>
          <ul class="activity-list">
            <li v-for="task in props.recentActivity" :key="task.id">
              <span class="activity-dot" :class="{ pending: task.isPending }"></span>
              <span class="task-title">{{ task.title }}</span>
              <small>{{ task.statusLabel }}</small>
            </li>
            <li v-if="!props.recentActivity.length" class="empty-row">Aun no hay actividad.</li>
          </ul>
        </section>
      </div>
    </section>
  </section>
</template>

<style scoped>
.dashboard-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.sidebar {
  padding: 12px 0 20px 20px;
}

.company-icon {
  width: 62px;
  height: 62px;
  display: block;
  margin-left: 5px;
  margin-bottom: 24px;
  object-fit: contain;
}

.nav-menu {
  display: grid;
  width: 182px;
}

.nav-item {
  display: grid;
  grid-template-columns: 56px 1fr;
  align-items: center;
  min-height: 52px;
  border: 0;
  border-right: 1px solid #75ddcb;
  border-bottom: 1px solid #75ddcb;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.nav-item.active {
  color: #715cff;
  font-weight: 700;
}

.nav-icon {
  width: 42px;
  display: inline-grid;
  place-items: center;
  color: #101010;
  font-size: 1.55rem;
}

.dashboard-content {
  min-width: 0;
  padding: 54px 74px 54px 60px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
}

.dashboard-header h1 {
  margin: 0;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.dashboard-header p {
  margin: 16px 0 0;
  font-size: 1.22rem;
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

.stats-row {
  max-width: 760px;
  margin-top: 26px;
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 28px;
  text-align: center;
}

.stats-row article {
  display: grid;
  gap: 12px;
}

.stats-row span {
  font-size: 1rem;
}

.stats-row strong {
  font-size: 2rem;
  font-weight: 500;
}

.stats-row .danger {
  color: #ff2d3b;
  font-weight: 800;
}

.stats-row .accent {
  color: #715cff;
  font-weight: 800;
}

.dashboard-grid {
  margin-top: 38px;
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(280px, 0.95fr);
  gap: 46px;
}

.panel h2 {
  margin: 0 0 24px;
  font-size: 1rem;
}

.task-list,
.activity-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.task-list li,
.activity-list li {
  min-height: 44px;
  display: grid;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.task-list li {
  grid-template-columns: 34px minmax(0, 1fr) auto;
  gap: 8px;
}

.activity-list li {
  grid-template-columns: 28px minmax(0, 1fr) 112px;
  gap: 8px;
}

.task-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-list time,
.activity-list small {
  color: #aeb0bb;
  font-size: 0.75rem;
}

.alert-icon {
  width: 26px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 3px solid #715cff;
  border-radius: 50%;
  color: #715cff;
  font-weight: 800;
}

.activity-dot {
  width: 20px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #8492df;
}

.activity-dot.pending {
  background: #e98383;
}

.empty-row,
.dashboard-error,
.loading-copy {
  color: #6d7180;
}

.dashboard-error {
  color: #e5333f;
}

@media (max-width: 860px) {
  .dashboard-frame {
    grid-template-columns: 1fr;
  }

  .sidebar {
    padding: 14px;
    border-bottom: 1px solid #75ddcb;
  }

  .company-icon {
    display: none;
  }

  .nav-menu {
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .nav-item {
    grid-template-columns: 34px 1fr;
    min-height: 44px;
  }

  .dashboard-content {
    padding: 28px 20px 36px;
  }

  .stats-row,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
