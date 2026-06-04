<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaTimeBlocking.vue"
Descripcion: Representa la planificación de bloques de tiempo.
-->

<script setup lang="ts">
import { computed, ref } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { TimeBlock } from './types'

const props = defineProps<{
  blocks: TimeBlock[]
  initials: string
  saving: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  'add-block': [block: Omit<TimeBlock, 'id'>]
  'remove-block': [blockId: number]
  finish: []
}>()

const blockForm = ref({
  title: '',
  start: '09:00',
  end: '10:00',
  category: 'Estudio',
})
const formMessage = ref('')

const colors = ['purple-block', 'green-block', 'yellow-block', 'blue-block', 'pink-block']
const hours = ['06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00']

const orderedBlocks = computed(() => [...props.blocks].sort((a, b) => a.start.localeCompare(b.start)))

function timeToMinutes(value: string) {
  const [hour = '0', minute = '0'] = value.split(':')
  return Number(hour) * 60 + Number(minute)
}

function submitBlock() {
  formMessage.value = ''
  const title = blockForm.value.title.trim()
  if (!title) {
    formMessage.value = 'Indica el nombre del bloque.'
    return
  }
  if (timeToMinutes(blockForm.value.end) <= timeToMinutes(blockForm.value.start)) {
    formMessage.value = 'La hora de fin debe ser posterior a la hora de inicio.'
    return
  }

  emit('add-block', {
    title,
    start: blockForm.value.start,
    end: blockForm.value.end,
    category: blockForm.value.category,
  })

  blockForm.value = {
    title: '',
    start: blockForm.value.end,
    end: nextHour(blockForm.value.end),
    category: blockForm.value.category,
  }
}

function nextHour(value: string) {
  const total = timeToMinutes(value) + 60
  const hour = Math.floor(total / 60) % 24
  const minute = total % 60
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
}
</script>

<template>
  <section class="blocking-frame">
    <MenuLateral active="tecnicas" @navigate="emit('navigate', $event)" />

    <section class="blocking-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <div class="blocking-header">
        <h1>Time blocking</h1>
        <p class="lead">Planifica tu día creando bloques con hora de inicio y fin</p>
        <p v-if="props.message" class="blocking-message">{{ props.message }}</p>
      </div>

      <div class="blocking-layout">
        <form class="block-form" @submit.prevent="submitBlock">
          <h2>Nuevo bloque</h2>
          <label>
            Título
            <input v-model.trim="blockForm.title" type="text" placeholder="Ej. Preparar entrega TFG" />
          </label>
          <div class="time-fields">
            <label>
              Inicio
              <input v-model="blockForm.start" type="time" />
            </label>
            <label>
              Fin
              <input v-model="blockForm.end" type="time" />
            </label>
          </div>
          <label>
            Categoría
            <select v-model="blockForm.category">
              <option>Estudio</option>
              <option>Trabajo</option>
              <option>Proyecto</option>
              <option>Personal</option>
              <option>Descanso</option>
            </select>
          </label>
          <p v-if="formMessage" class="form-message">{{ formMessage }}</p>
          <button class="new-block-button" type="submit" :disabled="props.saving">Añadir bloque</button>
        </form>

        <div class="schedule">
          <div class="schedule-toolbar">
            <button type="button" aria-label="Día anterior">‹</button>
            <strong>{{ new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date()) }}</strong>
            <button type="button" aria-label="Día siguiente">›</button>
            <span>Hoy</span>
          </div>

          <div class="timeline">
            <div class="hours-column">
              <span v-for="hour in hours" :key="hour">{{ hour }}</span>
            </div>

            <div class="blocks-column">
              <p v-if="!orderedBlocks.length" class="empty-blocks">
                Añade bloques para organizar tu jornada. Aquí no se muestran tareas inventadas.
              </p>
              <article
                v-for="(block, index) in orderedBlocks"
                :key="block.id"
                class="time-block"
                :class="colors[index % colors.length]"
              >
                <div>
                  <strong>{{ block.title }}</strong>
                  <small>{{ block.start }} - {{ block.end }}</small>
                </div>
                <em>{{ block.category }}</em>
                <button type="button" title="Eliminar bloque" @click="emit('remove-block', block.id)">Eliminar</button>
              </article>
            </div>
          </div>
        </div>
      </div>

      <div class="blocking-actions">
        <button class="finish-button" type="button" :disabled="props.saving" @click="emit('finish')">Finalizar estudio</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.blocking-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.blocking-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 76px 56px 74px 28px;
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

.blocking-header,
.blocking-layout,
.blocking-actions {
  width: min(100%, 1080px);
}

h1 {
  margin: 0;
  font-size: clamp(2.5rem, 5vw, 3.8rem);
  line-height: 1;
}

.lead {
  margin: 14px 0 22px;
  font-size: clamp(1.25rem, 2vw, 1.55rem);
}

.blocking-message,
.form-message {
  color: #e5333f;
}

.blocking-layout {
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.block-form {
  display: grid;
  gap: 12px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 18px;
}

.block-form h2 {
  margin: 0;
  font-size: 1.3rem;
}

.block-form label {
  display: grid;
  gap: 5px;
  font-weight: 700;
}

.block-form input,
.block-form select {
  height: 34px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 0 10px;
  font: inherit;
}

.time-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.schedule {
  min-width: 0;
  border: 1px solid #f0f0f2;
  background: #fff;
}

.schedule-toolbar {
  height: 46px;
  display: grid;
  grid-template-columns: 42px 1fr 42px 72px;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f0f0f2;
  padding: 0 12px;
  text-align: center;
  font-size: 1rem;
}

.schedule-toolbar button,
.schedule-toolbar span {
  min-height: 28px;
  border: 1px solid #e3e5ee;
  border-radius: 6px;
  background: #fff;
}

.timeline {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  gap: 0 14px;
  padding: 16px 18px;
}

.hours-column,
.blocks-column {
  display: grid;
  gap: 10px;
}

.hours-column span {
  min-height: 42px;
  color: #555967;
  font-size: 0.9rem;
}

.empty-blocks {
  min-height: 92px;
  display: grid;
  place-items: center;
  border: 1px dashed #715cff;
  border-radius: 8px;
  margin: 0;
  padding: 18px;
  color: #555967;
  text-align: center;
}

.time-block {
  min-height: 64px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  border-left: 6px solid currentColor;
  border-radius: 8px;
  padding: 12px 16px;
}

.time-block div {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.time-block strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 1rem;
}

.time-block small {
  color: #252943;
  font-size: 0.88rem;
}

.time-block em {
  border-radius: 999px;
  padding: 5px 12px;
  background: rgb(255 255 255 / 65%);
  font-size: 0.82rem;
  font-style: normal;
}

.time-block button {
  min-width: 82px;
  height: 30px;
  border: 1px solid #ff2d3b;
  border-radius: 999px;
  color: #ff2d3b;
  background: #fff;
  cursor: pointer;
}

.purple-block { color: #715cff; background: #f2edff; }
.green-block { color: #17a66a; background: #eaf8f0; }
.yellow-block { color: #e0a400; background: #fff8d8; }
.blue-block { color: #2386d1; background: #eaf5ff; }
.pink-block { color: #e94b7d; background: #ffeaf1; }

.blocking-actions {
  display: flex;
  justify-content: center;
  margin-top: 26px;
}

.finish-button,
.new-block-button {
  height: 42px;
  border-radius: 999px;
  font-size: 1rem;
  cursor: pointer;
}

.finish-button {
  min-width: 220px;
  border: 1.5px solid #ff2d3b;
  background: #fff;
}

.new-block-button {
  border: 0;
  color: #fff;
  background: #715cff;
}

button:disabled {
  opacity: 0.65;
  cursor: wait;
}

@media (max-width: 980px) {
  .blocking-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .blocking-frame {
    grid-template-columns: 1fr;
  }

  .blocking-content {
    min-height: calc(100vh - 8px);
    padding: 82px 20px 74px;
  }

  .schedule-toolbar {
    grid-template-columns: 34px 1fr 34px;
  }

  .schedule-toolbar span {
    display: none;
  }

  .timeline {
    grid-template-columns: 1fr;
  }

  .hours-column {
    display: none;
  }

  .time-block {
    grid-template-columns: 1fr;
  }
}
</style>
