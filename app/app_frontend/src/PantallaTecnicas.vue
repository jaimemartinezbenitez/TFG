<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaTecnicas.vue"
Descripcion: Representa el selector e historial de técnicas de productividad.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { ProductivitySession, ProductivityTechnique } from './types'

const props = defineProps<{
  initials: string
  loading: boolean
  message: string
  sessions: ProductivitySession[]
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'start-technique': [technique: ProductivityTechnique]
  'resume-session': [session: ProductivitySession]
}>()

const orderedSessions = computed(() =>
  [...props.sessions].sort(
    (a, b) => new Date(b.start_at).getTime() - new Date(a.start_at).getTime(),
  ),
)

const completedSessions = computed(() =>
  props.sessions.filter((session) => session.status === 'COMPLETED'),
)

const totalFocusMinutes = computed(() =>
  completedSessions.value.reduce((total, session) => total + session.effective_time, 0),
)

const totalCycles = computed(() =>
  completedSessions.value.reduce((total, session) => total + session.completed_cycles, 0),
)

const lastSession = computed(() => orderedSessions.value[0] || null)
const activeSessions = computed(() =>
  orderedSessions.value.filter((session) => session.status === 'IN_PROGRESS'),
)
const recentSessions = computed(() => orderedSessions.value.slice(0, 4))

const favoriteTechnique = computed(() => {
  const counts = completedSessions.value.reduce<Record<ProductivityTechnique, number>>(
    (accumulator, session) => {
      accumulator[session.technique] += 1
      return accumulator
    },
    { POMODORO: 0, TIME_BLOCKING: 0, FIFTY_TWO_SEVENTEEN: 0 },
  )

  const [technique, total] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0] as [
    ProductivityTechnique,
    number,
  ]

  return total > 0 ? techniqueLabel(technique) : 'Aún sin sesiones'
})

function techniqueLabel(technique: ProductivityTechnique) {
  const labels = {
    POMODORO: 'Pomodoro',
    TIME_BLOCKING: 'Time Blocking',
    FIFTY_TWO_SEVENTEEN: '52/17',
  }
  return labels[technique]
}

function techniquePurpose(technique: ProductivityTechnique) {
  const labels = {
    POMODORO: 'Trabajo breve con descansos frecuentes.',
    TIME_BLOCKING: 'Organización del día en bloques concretos.',
    FIFTY_TWO_SEVENTEEN: 'Sesiones largas para tareas exigentes.',
  }
  return labels[technique]
}

function statusLabel(status: ProductivitySession['status']) {
  const labels = {
    IN_PROGRESS: 'En curso',
    COMPLETED: 'Completada',
    INTERRUPTED: 'Interrumpida',
  }
  return labels[status]
}

function durationLabel(minutes: number) {
  if (!minutes) return '0m'
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (!hours) return `${remainingMinutes}m`
  if (!remainingMinutes) return `${hours}h`
  return `${hours}h ${remainingMinutes}m`
}

function dateLabel(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function elapsedLabel(value: string) {
  const elapsedMinutes = Math.max(Math.floor((Date.now() - new Date(value).getTime()) / 60000), 0)
  return durationLabel(elapsedMinutes)
}
</script>

<template>
  <section class="techniques-frame">
    <MenuLateral active="tecnicas" @navigate="emit('navigate', $event)" />

    <section class="techniques-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <header class="techniques-header">
        <h1>Técnicas de productividad</h1>
        <p class="lead">Registra sesiones de concentración y convierte el tiempo trabajado en métricas de productividad.</p>
        <p v-if="props.message" class="technique-message">{{ props.message }}</p>
      </header>

      <section class="technique-flow" aria-label="Funcionamiento de las sesiones de productividad">
        <article>
          <strong>1</strong>
          <span>Elige una técnica</span>
        </article>
        <article>
          <strong>2</strong>
          <span>Trabaja con el temporizador o con bloques</span>
        </article>
        <article>
          <strong>3</strong>
          <span>La sesión se guarda en estadísticas y logros</span>
        </article>
      </section>

      <section v-if="activeSessions.length" class="active-sessions" aria-label="Sesiones en curso">
        <div class="active-sessions-title">
          <h2>Sesiones en curso</h2>
          <span>{{ activeSessions.length }} sin finalizar</span>
        </div>
        <ul>
          <li v-for="session in activeSessions" :key="session.id">
            <div>
              <strong>{{ techniqueLabel(session.technique) }}</strong>
              <span>Iniciada {{ dateLabel(session.start_at) }} · {{ elapsedLabel(session.start_at) }} transcurridos</span>
            </div>
            <button type="button" :disabled="props.loading" @click="emit('resume-session', session)">
              Retomar
            </button>
          </li>
        </ul>
      </section>

      <div class="technique-grid">
        <article class="technique-card">
          <div class="technique-icon tomato-icon" aria-hidden="true"><span>25:00</span></div>
          <h2>Pomodoro</h2>
          <p>25 minutos de concentración y 5 minutos de descanso para avanzar en tareas cortas.</p>
          <small>{{ techniquePurpose('POMODORO') }}</small>
          <button type="button" :disabled="props.loading" @click="emit('start-technique', 'POMODORO')">Iniciar</button>
        </article>

        <article class="technique-card">
          <div class="technique-icon clock-icon" aria-hidden="true"></div>
          <h2>Time Blocking</h2>
          <p>Planifica franjas horarias, asigna una actividad a cada bloque y registra el tiempo total.</p>
          <small>{{ techniquePurpose('TIME_BLOCKING') }}</small>
          <button type="button" :disabled="props.loading" @click="emit('start-technique', 'TIME_BLOCKING')">Iniciar</button>
        </article>

        <article class="technique-card">
          <div class="technique-icon cycle-icon" aria-hidden="true"><span>52/17</span></div>
          <h2>52/17</h2>
          <p>52 minutos de trabajo profundo y 17 minutos de descanso para sesiones largas.</p>
          <small>{{ techniquePurpose('FIFTY_TWO_SEVENTEEN') }}</small>
          <button type="button" :disabled="props.loading" @click="emit('start-technique', 'FIFTY_TWO_SEVENTEEN')">Iniciar</button>
        </article>
      </div>

      <section class="history-section" aria-label="Información sobre técnicas anteriores">
        <div class="history-summary">
          <article class="summary-item">
            <strong>{{ completedSessions.length }}</strong>
            <span>sesiones completadas</span>
          </article>
          <article class="summary-item">
            <strong>{{ durationLabel(totalFocusMinutes) }}</strong>
            <span>tiempo de enfoque</span>
          </article>
          <article class="summary-item">
            <strong>{{ totalCycles }}</strong>
            <span>ciclos completados</span>
          </article>
          <article class="summary-item">
            <strong>{{ favoriteTechnique }}</strong>
            <span>técnica más usada</span>
          </article>
        </div>

        <div class="history-list">
          <div class="history-title-row">
            <h2>Sesiones anteriores</h2>
            <span v-if="lastSession">Última: {{ techniqueLabel(lastSession.technique) }}</span>
          </div>

          <p v-if="!recentSessions.length" class="empty-history">
            Al finalizar una técnica, aquí aparecerá el historial de tus sesiones.
          </p>

          <table v-else>
            <thead>
              <tr>
                <th>Técnica</th>
                <th>Estado</th>
                <th>Enfoque</th>
                <th>Ciclos</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="session in recentSessions" :key="session.id">
                <td>{{ techniqueLabel(session.technique) }}</td>
                <td>
                  <span class="status-pill" :class="`status-${session.status.toLowerCase()}`">
                    {{ statusLabel(session.status) }}
                  </span>
                </td>
                <td>{{ durationLabel(session.effective_time) }}</td>
                <td>{{ session.completed_cycles }}</td>
                <td>{{ dateLabel(session.start_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </section>
</template>

<style scoped>
.techniques-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.techniques-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 86px 52px 74px 24px;
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

.techniques-header {
  width: min(100%, 1060px);
  text-align: center;
}

h1 {
  margin: 0;
  font-size: clamp(2.3rem, 4.5vw, 3.25rem);
  line-height: 1;
}

.lead {
  margin: 16px auto 10px;
  font-size: 1.28rem;
  line-height: 1.25;
}

.technique-message {
  color: #e5333f;
}

.technique-flow {
  width: min(100%, 1040px);
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.technique-flow article {
  min-height: 72px;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fbfffe;
  padding: 12px 14px;
}

.technique-flow strong {
  width: 34px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #fff;
  background: #715cff;
}

.technique-flow span {
  color: #34384a;
  font-weight: 800;
}

.active-sessions {
  width: min(100%, 1040px);
  margin-top: 24px;
}

.active-sessions-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.active-sessions-title h2 {
  margin: 0;
  font-size: 1.35rem;
}

.active-sessions-title span {
  color: #715cff;
  font-weight: 800;
}

.active-sessions ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.active-sessions li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  gap: 18px;
  align-items: center;
  border-left: 4px solid #715cff;
  border-bottom: 1px solid #75ddcb;
  padding: 10px 0 10px 14px;
  background: #f5f2ff;
}

.active-sessions li div {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.active-sessions li span {
  color: #555967;
  font-size: 0.9rem;
}

.active-sessions button {
  height: 34px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
}

.active-sessions button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.technique-grid {
  width: min(100%, 1040px);
  margin-top: 26px;
  display: grid;
  grid-template-columns: repeat(3, minmax(220px, 1fr));
  gap: 62px;
  text-align: center;
}

.technique-card {
  display: grid;
  justify-items: center;
  align-content: start;
  min-height: 390px;
  border: 1.5px solid #75ddcb;
  border-radius: 8px;
  background: #fff;
  padding: 22px 18px;
}

.technique-icon {
  width: 178px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  margin-bottom: 16px;
}

.tomato-icon {
  border: 12px solid #ec2f88;
  border-radius: 50%;
  color: #ff7a22;
  font-weight: 900;
  font-size: 1.7rem;
  box-shadow: inset 0 0 0 10px #ffd5e8;
}

.clock-icon {
  position: relative;
  border: 13px solid #075985;
  border-radius: 50%;
}

.clock-icon::before {
  content: "";
  width: 52px;
  height: 5px;
  background: #075985;
  transform: translate(22px, 0);
}

.clock-icon::after {
  content: "";
  position: absolute;
  width: 5px;
  height: 58px;
  background: #075985;
  transform: translateY(-24px);
}

.cycle-icon {
  border: 11px solid #715cff;
  border-right-color: transparent;
  border-radius: 50%;
  color: #715cff;
  font-size: 2.05rem;
  font-weight: 900;
}

.technique-card h2 {
  margin: 0;
  font-size: 1.38rem;
}

.technique-card p {
  min-height: 76px;
  margin: 10px 0 8px;
  font-size: 1.05rem;
  line-height: 1.35;
}

.technique-card small {
  min-height: 38px;
  color: #6d7180;
  font-weight: 700;
}

.technique-card button {
  width: 150px;
  height: 36px;
  margin-top: 22px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  font-size: 1rem;
  cursor: pointer;
}

.technique-card button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.history-section {
  width: min(100%, 1040px);
  display: grid;
  grid-template-columns: minmax(260px, 360px) minmax(0, 1fr);
  gap: 34px;
  margin-top: 22px;
  align-items: start;
}

.history-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  min-height: 98px;
  display: grid;
  align-content: center;
  gap: 5px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 14px;
  color: #715cff;
  text-align: center;
}

.summary-item strong {
  font-size: 1.85rem;
  line-height: 1;
}

.summary-item span {
  font-size: 0.9rem;
}

.history-list {
  min-width: 0;
}

.history-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.history-title-row h2 {
  margin: 0;
  font-size: 1.5rem;
}

.history-title-row span {
  color: #715cff;
  font-weight: 800;
}

.empty-history {
  margin: 0;
  border-left: 4px solid #715cff;
  padding: 12px 14px;
  background: #f3f0ff;
  color: #34384a;
  font-weight: 700;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid #73e2ce;
  padding: 10px 12px;
  text-align: left;
}

th {
  font-size: 0.95rem;
}

.status-pill {
  font-size: 0.82rem;
  font-weight: 900;
}

.status-completed {
  color: #3f6cff;
}

.status-in_progress {
  color: #00b865;
}

.status-interrupted {
  color: #ff303c;
}

@media (max-width: 1120px) {
  .technique-grid,
  .history-section,
  .technique-flow {
    width: min(100%, 860px);
  }

  .technique-grid {
    gap: 32px;
  }

  .technique-icon {
    width: 150px;
  }
}

@media (max-width: 920px) {
  .techniques-frame {
    grid-template-columns: 1fr;
  }

  .techniques-content {
    padding: 82px 20px 74px;
  }

  .active-sessions li {
    grid-template-columns: 1fr;
  }

  .technique-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .technique-flow {
    grid-template-columns: 1fr;
  }

  .technique-card {
    min-height: auto;
  }

  .history-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .history-summary {
    grid-template-columns: 1fr;
  }

  table {
    font-size: 0.86rem;
  }

  th,
  td {
    padding: 8px 6px;
  }
}
</style>
