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
  'finish-break': []
}>()

const timeLabel = computed(() => {
  const minutes = Math.floor(props.timer.remainingSeconds / 60)
  const seconds = props.timer.remainingSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const progressDegrees = computed(() => {
  const total = props.timer.breakMinutes * 60
  const elapsed = Math.max(total - props.timer.remainingSeconds, 0)
  return `${Math.min((elapsed / total) * 360, 360)}deg`
})

const cycleLabel = computed(() => `${props.timer.completedCycles}/${props.timer.targetCycles}`)
</script>

<template>
  <section class="break-frame">
    <MenuLateral active="tecnicas" @navigate="emit('navigate', $event)" />

    <section class="break-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>Pomodoro</h1>
      <p class="lead">¡Buen trabajo, tómate un descanso!</p>

      <div class="break-card">
        <div class="timer-circle" :style="{ '--progress': progressDegrees }">
          <span class="cup" aria-hidden="true">☕</span>
          <strong>{{ timeLabel }}</strong>
          <small>Tiempo restante</small>
        </div>
        <p class="cycle-copy">Descanso {{ cycleLabel }}</p>

        <button class="finish-break-button" type="button" @click="emit('finish-break')">
          Finalizar descanso <span aria-hidden="true">▶▶</span>
        </button>
        <button class="pause-button" type="button" @click="props.timer.isRunning ? emit('pause') : emit('resume')">
          {{ props.timer.isRunning ? 'Pausar descanso' : 'Continuar descanso' }}
        </button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.break-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.break-content {
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
  margin: 14px 0 24px;
  font-size: clamp(1.25rem, 2vw, 1.55rem);
}

.break-card {
  width: min(100%, 660px);
  display: grid;
  justify-items: center;
  gap: 20px;
}

.timer-circle {
  --progress: 0deg;
  width: clamp(280px, 28vw, 370px);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background:
    radial-gradient(#fff 58%, transparent 59%),
    conic-gradient(#2fbb72 var(--progress), #ddf5e8 0deg);
}

.cup {
  align-self: end;
  font-size: clamp(2.2rem, 3.3vw, 3.1rem);
}

.timer-circle strong {
  color: #0d1430;
  font-size: clamp(3.6rem, 6vw, 5.3rem);
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

.finish-break-button {
  border: 0;
  color: #715cff;
  background: transparent;
  font-size: clamp(1.35rem, 2.2vw, 1.8rem);
  font-weight: 900;
  cursor: pointer;
}

.finish-break-button span {
  margin-left: 12px;
  font-size: clamp(2.2rem, 3vw, 3rem);
  vertical-align: middle;
}

.pause-button {
  width: min(100%, 260px);
  height: 42px;
  border: 1px solid #2fbb72;
  border-radius: 8px;
  color: #15804a;
  background: #fff;
  font-size: 1rem;
  cursor: pointer;
}

@media (max-width: 860px) {
  .break-frame {
    grid-template-columns: 1fr;
  }

  .break-content {
    min-height: calc(100vh - 8px);
    padding: 82px 20px 74px;
  }
}
</style>

