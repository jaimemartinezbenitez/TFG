<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
import type { ProjectForm } from './types'

const props = defineProps<{
  form: ProjectForm
  initials: string
  loading: boolean
  message: string
  mode: 'create' | 'edit'
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  submit: []
  cancel: []
}>()
</script>

<template>
  <section class="project-form-frame">
    <MenuLateral active="proyecto" @navigate="emit('navigate', $event)" />

    <section class="project-form-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <h1>{{ props.mode === 'create' ? 'Crear proyecto' : 'Editar proyecto' }}</h1>
      <h2>{{ props.mode === 'create' ? 'Nuevo proyecto' : props.form.name || 'Proyecto' }}</h2>

      <form class="project-form" @submit.prevent="emit('submit')">
        <div class="left-fields">
          <label for="projectName">Título</label>
          <input id="projectName" v-model.trim="props.form.name" required maxlength="80" placeholder="Nombre del proyecto" />

          <label for="projectDescription">Descripción</label>
          <textarea id="projectDescription" v-model.trim="props.form.description" placeholder="Describe el proyecto..."></textarea>
        </div>

        <div class="right-fields">
          <label for="projectStart">Fecha inicio</label>
          <input id="projectStart" v-model="props.form.start_date" type="date" />

          <label for="projectEnd">Fecha finalización</label>
          <input id="projectEnd" v-model="props.form.end_date" type="date" />
        </div>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <div class="form-actions">
          <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">Cancelar</button>
          <button class="save-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Guardando...' : 'Guardar proyecto' }}
          </button>
        </div>
      </form>
    </section>
  </section>
</template>

<style scoped>
.project-form-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.project-form-content {
  position: relative;
  min-width: 0;
  padding: 54px 40px 74px 34px;
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
  margin: 0 0 30px;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

h2 {
  margin: 0 0 14px;
  font-size: 1.35rem;
}

.project-form {
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
textarea {
  width: 100%;
  border: 2px solid #7161ff;
  border-radius: 8px;
  background: #fff;
  outline: none;
}

input {
  height: 30px;
  padding: 0 8px;
}

textarea {
  min-height: 132px;
  resize: vertical;
  padding: 8px;
}

input::placeholder,
textarea::placeholder {
  color: #b8bac4;
  font-style: italic;
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
  .project-form {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .form-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .project-form-frame {
    grid-template-columns: 1fr;
  }

  .project-form-content {
    padding: 82px 20px 74px;
  }
}
</style>
