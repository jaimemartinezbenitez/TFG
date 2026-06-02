<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
import type { Task } from './types'

const props = defineProps<{
  task: Task | null
  tasks: Task[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  cancel: []
  confirm: []
}>()

function formatDate(value: string | null) {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES').format(new Date(`${value}T00:00:00`))
}
</script>

<template>
  <section class="delete-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="delete-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>Mis tareas</h1>
      <div class="muted-table" aria-hidden="true">
        <div v-for="taskItem in props.tasks.slice(0, 6)" :key="taskItem.id" class="muted-row">
          <span>{{ taskItem.title }}</span>
          <strong>{{ formatDate(taskItem.due_date) }}</strong>
          <button type="button">Eliminar</button>
        </div>
      </div>

      <div class="backdrop"></div>

      <section class="delete-modal" role="dialog" aria-modal="true" aria-labelledby="deleteTitle">
          <h2 id="deleteTitle">Eliminar tarea</h2>
        <p v-if="props.task">
          Estás seguro que quieres eliminar<br />
          la tarea <strong>“{{ props.task.title }}”</strong>?
        </p>
        <p v-else>No se ha encontrado la tarea seleccionada.</p>
        <h3>Esta acción es irreversible</h3>
        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <div class="modal-actions">
          <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">Cancelar</button>
          <button class="delete-button" type="button" :disabled="props.loading || !props.task" @click="emit('confirm')">
            {{ props.loading ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </section>
    </section>
  </section>
</template>

<style scoped>
.delete-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.delete-content {
  position: relative;
  min-width: 0;
  padding: 62px 24px 74px 52px;
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
  margin: 0 0 34px;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

.muted-table {
  width: min(100%, 790px);
  display: grid;
  opacity: 0.32;
  filter: grayscale(1);
}

.muted-row {
  min-height: 41px;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 150px 110px;
  align-items: center;
  border-bottom: 1px solid #75ddcb;
}

.muted-row button {
  height: 30px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #a7a7a7;
}

.backdrop {
  position: absolute;
  inset: 0;
  background: rgb(0 0 0 / 15%);
}

.delete-modal {
  position: absolute;
  top: 104px;
  left: 50%;
  width: min(710px, calc(100% - 48px));
  min-height: 400px;
  display: grid;
  align-content: start;
  justify-items: center;
  border: 2px solid #101010;
  border-radius: 20px;
  background: #fff;
  padding: 36px 38px;
  transform: translateX(-50%);
}

.delete-modal h2 {
  margin: 0 0 24px;
  font-size: clamp(2.7rem, 4.8vw, 3.35rem);
}

.delete-modal p {
  margin: 0;
  font-size: 1.55rem;
  line-height: 1.35;
}

.delete-modal strong {
  color: #ff2d3b;
}

.delete-modal h3 {
  width: min(100%, 370px);
  margin: 0;
  font-size: 1.55rem;
}

.form-message {
  margin-top: 16px;
  color: #e5333f;
  font-size: 0.95rem;
}

.modal-actions {
  width: min(100%, 372px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 172px));
  justify-content: center;
  gap: 30px;
  margin-top: 52px;
}

.cancel-button,
.delete-button {
  height: 34px;
  border-radius: 999px;
  cursor: pointer;
}

.cancel-button {
  border: 1.5px solid #101010;
  background: #fff;
}

.delete-button {
  border: 0;
  color: #fff;
  background: #ff2d3b;
}

.cancel-button:disabled,
.delete-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

@media (max-width: 860px) {
  .delete-frame {
    grid-template-columns: 1fr;
  }

  .delete-content {
    padding: 82px 16px 74px;
  }

  .delete-modal {
    position: relative;
    top: auto;
    left: auto;
    margin: 20px auto 0;
    transform: none;
  }
}
</style>
