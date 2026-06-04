<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaExportarDatos.vue"
Descripcion: Representa la pantalla para exportar datos en CSV o PDF.
-->

<script setup lang="ts">
import { computed } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { ExportForm, Project } from './types'

const props = defineProps<{
  form: ExportForm
  projects: Project[]
  initials: string
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
  submit: []
}>()

const orderedProjects = computed(() =>
  [...props.projects].sort((first, second) => first.name.localeCompare(second.name)),
)
</script>

<template>
  <section class="export-frame">
    <MenuLateral active="exportar" @navigate="emit('navigate', $event)" />

    <section class="export-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <div class="export-panel">
        <header class="export-header">
          <h1>Exportar datos</h1>
          <p class="export-copy">Descarga perfil, métricas, tareas y sesiones en el formato que prefieras</p>
        </header>

        <form class="export-form" @submit.prevent="emit('submit')">
          <label for="exportDeadline">Fecha límite</label>
          <input id="exportDeadline" v-model="props.form.deadline" type="date" />

          <label for="exportProject">Proyecto</label>
          <select id="exportProject" v-model="props.form.project">
            <option value="">Seleccionar proyecto...</option>
            <option v-for="project in orderedProjects" :key="project.id" :value="String(project.id)">
              {{ project.name }}
            </option>
          </select>

          <fieldset>
            <legend>Formato</legend>
            <label class="radio-option">
              <input v-model="props.form.format" type="radio" value="csv" />
              <span>CSV</span>
            </label>
            <label class="radio-option">
              <input v-model="props.form.format" type="radio" value="pdf" />
              <span>PDF</span>
            </label>
          </fieldset>

          <p v-if="props.message" class="export-message">{{ props.message }}</p>

          <button class="download-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Preparando descarga...' : 'Generar y descargar' }}
          </button>
        </form>
      </div>
    </section>
  </section>
</template>

<style scoped>
.export-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.export-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  display: flex;
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

.export-panel {
  width: min(100%, 760px);
  display: grid;
  gap: 26px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: clamp(28px, 5vw, 46px);
}

.export-header {
  display: grid;
  gap: 14px;
}

h1 {
  margin: 0;
  font-size: clamp(2.7rem, 5vw, 4.2rem);
  line-height: 1;
}

.export-copy {
  max-width: 560px;
  margin: 0;
  font-size: clamp(1.2rem, 2vw, 1.55rem);
  line-height: 1.35;
}

.export-form {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 14px;
}

label,
legend {
  font-size: 1.16rem;
  font-weight: 700;
}

input,
select {
  width: 100%;
  height: 42px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  background: #fff;
  outline: none;
  font-size: 1.02rem;
}

input {
  padding: 0 12px;
}

select {
  padding: 0 42px 0 12px;
  color: #050505;
}

select:invalid,
select option[value=''] {
  color: #b8bac4;
  font-style: italic;
}

fieldset {
  display: flex;
  flex-wrap: wrap;
  gap: 34px;
  margin: 4px 0 0;
  padding: 0;
  border: 0;
}

legend {
  width: 100%;
  margin-bottom: 0;
}

.radio-option {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  min-width: 96px;
  cursor: pointer;
}

.radio-option input {
  width: 26px;
  height: 26px;
  margin: 0;
  accent-color: #715cff;
}

.radio-option span {
  font-size: 1.08rem;
  font-weight: 500;
}

.export-message {
  margin: 2px 0 0;
  color: #e5333f;
}

.download-button {
  justify-self: center;
  width: min(100%, 320px);
  height: 42px;
  margin-top: 12px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #715cff;
  cursor: pointer;
  font-size: 1.02rem;
}

.download-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

@media (max-width: 860px) {
  .export-frame {
    grid-template-columns: 1fr;
  }

  .export-content {
    min-height: auto;
    padding: 86px 20px 74px;
  }
}

@media (max-width: 520px) {
  .avatar-button {
    width: 54px;
    right: 16px;
  }

  .download-button {
    justify-self: stretch;
  }
}
</style>
