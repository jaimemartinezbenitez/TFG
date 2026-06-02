<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
import type { Project, TaskForm } from './types'

const props = defineProps<{
  form: TaskForm
  projects: Project[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  submit: []
  cancel: []
}>()
</script>

<template>
  <section class="task-form-frame">
    <MenuLateral active="tareas" @navigate="emit('navigate', $event)" />

    <section class="task-form-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>Crear tarea</h1>
      <h2>Nueva tarea</h2>

      <form class="task-form" @submit.prevent="emit('submit')">
        <div class="left-fields">
          <label for="taskTitle">Título</label>
          <input id="taskTitle" v-model.trim="props.form.title" required maxlength="50" placeholder="Nombre de la tarea" />

          <label for="taskDescription">Descripción</label>
          <textarea id="taskDescription" v-model.trim="props.form.description" placeholder="Describe la tarea..."></textarea>
        </div>

        <div class="right-fields">
          <label for="taskDate">Fecha límite</label>
          <input id="taskDate" v-model="props.form.due_date" type="date" />

          <label for="taskPriority">Prioridad</label>
          <select id="taskPriority" v-model="props.form.priority">
            <option value="HIGH">ALTA</option>
            <option value="MEDIUM">MEDIA</option>
            <option value="LOW">BAJA</option>
          </select>

          <label for="taskProject">Proyecto</label>
          <select id="taskProject" v-model="props.form.project">
            <option value="">Seleccionar proyecto...</option>
            <option v-for="project in props.projects" :key="project.id" :value="String(project.id)">
              {{ project.name }}
            </option>
          </select>
        </div>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <div class="form-actions">
          <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">Cancelar</button>
          <button class="save-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Guardando...' : 'Guardar tarea' }}
          </button>
        </div>
      </form>
    </section>
  </section>
</template>

<style scoped>
.task-form-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.task-form-content {
  position: relative;
  min-width: 0;
  padding: 62px 40px 74px 34px;
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
  margin: 0 0 8px;
  font-size: clamp(2.85rem, 5vw, 3.65rem);
  line-height: 1;
}

h2 {
  margin: 0 0 14px;
  font-size: 1.35rem;
}

.task-form {
  max-width: 660px;
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(240px, 0.95fr);
  gap: 28px 112px;
}

.left-fields,
.right-fields {
  display: grid;
  align-content: start;
  gap: 10px;
}

label {
  font-size: 1.05rem;
}

input,
textarea,
select {
  width: 100%;
  border: 2px solid #7161ff;
  border-radius: 8px;
  background: #fff;
  outline: none;
}

input,
select {
  height: 30px;
  padding: 0 8px;
}

textarea {
  min-height: 132px;
  resize: vertical;
  padding: 8px;
}

input::placeholder,
textarea::placeholder,
select:invalid {
  color: #b8bac4;
  font-style: italic;
}

select {
  cursor: pointer;
}

.form-message {
  grid-column: 1 / -1;
  margin: 0;
  color: #e5333f;
}

.form-actions {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 170px 220px;
  justify-content: center;
  gap: 30px;
  margin-top: 8px;
}

.cancel-button,
.save-button {
  height: 34px;
  border-radius: 999px;
  cursor: pointer;
}

.cancel-button {
  border: 1.5px solid #101010;
  background: #fff;
}

.save-button {
  border: 0;
  color: #fff;
  background: #715cff;
}

.cancel-button:disabled,
.save-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

@media (max-width: 900px) {
  .task-form {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .form-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .task-form-frame {
    grid-template-columns: 1fr;
  }

  .task-form-content {
    padding: 82px 20px 74px;
  }
}
</style>
