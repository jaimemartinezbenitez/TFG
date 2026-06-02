<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { TechniqueTimerState } from './types'

const props = defineProps<{
  timer: TechniqueTimerState
  initials: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  pause: []
  resume: []
  cancel: []
  finish: []
}>()

const timeLabel = computed(() => {
  const minutes = Math.floor(props.timer.remainingSeconds / 60)
  const seconds = props.timer.remainingSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const progressDegrees = computed(() => {
  const total = props.timer.workMinutes * 60
  const elapsed = Math.max(total - props.timer.remainingSeconds, 0)
  return `${Math.min((elapsed / total) * 360, 360)}deg`
})

const cycleLabel = computed(() => `${props.timer.currentCycle}/${props.timer.targetCycles}`)
</script>

<template>
  <section class="timer-frame">
    <MenuLateral active="tecnicas" @navigate="emit('navigate', $event)" />

    <section class="timer-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>52-17</h1>
      <p class="lead">¡Mantén el foco!</p>

      <div class="timer-card">
        <span class="phase-pill">Sesión de enfoque</span>
        <div class="timer-circle " :style="{ '--progress': progressDegrees }">
          <span class="technique-symbol">52/17</span>
          <strong>{{ timeLabel }}</strong>
          <small>Tiempo restante</small>
        </div>

        <p class="cycle-copy">Ciclo {{ cycleLabel }}</p>

        <div class="suggestion">
          <strong>Objetivo sugerido</strong>
          <span>Tareas que requieren máxima concentración y pensamiento profundo.</span>
        </div>

        <div class="timer-actions">
          <button class="secondary-button" type="button" @click="emit('cancel')">Cancelar</button>
          <button class="primary-button" type="button" @click="props.timer.isRunning ? emit('pause') : emit('resume')">
            {{ props.timer.isRunning ? 'Pausar' : 'Continuar' }}
          </button>
          <button class="secondary-button" type="button" @click="emit('finish')">Finalizar</button>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.timer-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.timer-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 76px 56px 74px 28px;
  text-align: center;
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
  margin: 0;
  font-size: clamp(2.5rem, 5vw, 3.8rem);
  line-height: 1;
}

.lead {
  margin: 14px 0 20px;
  font-size: clamp(1.25rem, 2vw, 1.55rem);
}

.timer-card {
  width: min(100%, 720px);
  display: grid;
  justify-items: center;
  gap: 20px;
}

.phase-pill {
  border-radius: 999px;
  padding: 7px 18px;
  color: #0f8f55;
  background: #dff8eb;
  font-size: 0.95rem;
  font-weight: 800;
}

.timer-circle {
  --progress: 0deg;
  width: clamp(270px, 27vw, 360px);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background:
    radial-gradient(#fff 58%, transparent 59%),
    conic-gradient(#715cff var(--progress), #eee8ff 0deg);
}

.pomodoro-theme {
  background:
    radial-gradient(#fff 58%, transparent 59%),
    conic-gradient(#ff303c var(--progress), #ffd6dc 0deg);
}

.technique-symbol {
  align-self: end;
  font-size: clamp(2rem, 3.3vw, 3rem);
  font-weight: 900;
}

.timer-circle strong {
  color: #0d1430;
  font-size: clamp(3.8rem, 6.5vw, 5.6rem);
  line-height: 1;
}

.timer-circle small {
  align-self: start;
  border-radius: 999px;
  padding: 5px 12px;
  color: #6d7180;
  background: #f3f2fa;
  font-size: 0.9rem;
}

.cycle-copy {
  margin: 0;
  color: #715cff;
  font-size: clamp(1.35rem, 2.2vw, 1.8rem);
  font-weight: 900;
}

.suggestion {
  width: min(100%, 660px);
  display: grid;
  gap: 6px;
  border-radius: 8px;
  padding: 18px 22px;
  color: #252943;
  background: #f5f2ff;
  font-size: 1rem;
  text-align: left;
}

.suggestion span {
  color: #555967;
  font-size: 0.92rem;
}

.timer-actions {
  width: min(100%, 660px);
  display: grid;
  grid-template-columns: repeat(3, minmax(140px, 1fr));
  gap: 20px;
}

.primary-button,
.secondary-button {
  height: 44px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.primary-button {
  border: 0;
  color: #fff;
  background: #715cff;
}

.secondary-button {
  border: 1px solid #dddfea;
  background: #fff;
}

@media (max-width: 860px) {
  .timer-frame {
    grid-template-columns: 1fr;
  }

  .timer-content {
    min-height: calc(100vh - 8px);
    padding: 82px 20px 74px;
  }

  .timer-actions {
    grid-template-columns: 1fr;
  }
}
</style>

