<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaResumenPomodoro.vue"
Descripcion: Representa el resumen final de una sesión Pomodoro.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { TechniqueTimerState } from './types'

const props = defineProps<{
  timer: TechniqueTimerState
  initials: string
  saving: boolean
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  finish: []
  restart: []
}>()

const focusLabel = computed(() => formatDuration(props.timer.effectiveSeconds))
const breakLabel = computed(() => formatDuration(props.timer.breakSeconds))

function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.round((seconds % 3600) / 60)
  if (hours && minutes) return `${hours}h ${minutes}m`
  if (hours) return `${hours}h`
  return `${minutes}m`
}
</script>

<template>
  <section class="summary-frame">
    <MenuLateral active="tecnicas" @navigate="emit('navigate', $event)" />

    <section class="summary-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>Resumen de sesión</h1>
      <div class="summary-cards">
        <article>
          <strong>{{ props.timer.completedCycles }}</strong>
          <span>POMODOROS<br />completados</span>
        </article>
        <article>
          <strong>{{ props.timer.completedCycles ? '100%' : '0%' }}</strong>
          <span>Enfoque total</span>
        </article>
        <article>
          <strong>{{ focusLabel }}</strong>
          <span>Tiempo de<br />enfoque</span>
        </article>
        <article>
          <strong>{{ breakLabel }}</strong>
          <span>Tiempo de<br />descanso</span>
        </article>
      </div>

      <div class="summary-actions">
        <button class="finish-button" type="button" :disabled="props.saving" @click="emit('finish')">Finalizar estudio</button>
        <button class="restart-button" type="button" :disabled="props.saving" @click="emit('restart')">Volver a empezar</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.summary-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.summary-content {
  position: relative;
  min-width: 0;
  padding: 96px 52px 74px;
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

h1 {
  margin: 0 0 28px;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.summary-cards {
  width: min(100%, 612px);
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 14px;
}

.summary-cards article {
  min-height: 194px;
  display: grid;
  place-items: center;
  border: 2px solid #7161ff;
  border-radius: 8px;
  color: #715cff;
  text-align: center;
}

.summary-cards strong {
  align-self: end;
  font-size: 2.2rem;
}

.summary-cards span {
  align-self: start;
  font-size: 0.98rem;
}

.summary-actions {
  width: min(100%, 420px);
  display: grid;
  grid-template-columns: 170px 220px;
  gap: 22px;
  margin: 58px 0 0 122px;
}

.finish-button,
.restart-button {
  height: 34px;
  border-radius: 999px;
  cursor: pointer;
}

.finish-button {
  border: 1.5px solid #ff2d3b;
  color: #050505;
  background: #fff;
}

.restart-button {
  border: 0;
  color: #fff;
  background: #715cff;
}

button:disabled {
  opacity: 0.65;
  cursor: wait;
}

@media (max-width: 900px) {
  .summary-frame {
    grid-template-columns: 1fr;
  }

  .summary-content {
    padding: 82px 20px 74px;
  }

  .summary-cards,
  .summary-actions {
    grid-template-columns: 1fr;
    margin-left: 0;
  }
}
</style>
