<script setup lang="ts">
type MenuSection =
  | 'inicio'
  | 'tareas'
  | 'proyecto'
  | 'calendario'
  | 'tecnicas'
  | 'estadisticas'
  | 'logros'
  | 'exportar'

const props = defineProps<{
  active?: MenuSection
}>()

const emit = defineEmits<{
  navigate: [section: MenuSection]
}>()

const items: Array<{ id: MenuSection; label: string; icon: string }> = [
  { id: 'inicio', label: 'Inicio', icon: '/icono-inicio.png' },
  { id: 'tareas', label: 'Tareas', icon: '/icono-tareas.png' },
  { id: 'proyecto', label: 'Proyecto', icon: '/icono-proyecto.png' },
  { id: 'calendario', label: 'Calendario', icon: '/icono-calendario.png' },
  { id: 'tecnicas', label: 'Tecnicas', icon: '/icono-tecnicas.png' },
  { id: 'estadisticas', label: 'Estadisticas', icon: '/icono-estadisticas.png' },
  { id: 'logros', label: 'Logros', icon: '/icono-logros.png' },
  { id: 'exportar', label: 'Exportar datos', icon: '/icono-exportardatos.png' },
]
</script>

<template>
  <aside class="sidebar">
    <img class="company-icon" src="/icono.png" alt="ConcentraPlus" />

    <nav class="nav-menu" aria-label="Navegacion principal">
      <button
        v-for="item in items"
        :key="item.id"
        class="nav-item"
        :class="{ active: props.active === item.id }"
        type="button"
        @click="emit('navigate', item.id)"
      >
        <img class="nav-icon-img" :src="item.icon" alt="" aria-hidden="true" />
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 204px;
  min-width: 204px;
  min-height: 100%;
  align-self: stretch;
  padding: 12px 0 20px 20px;
}

.company-icon {
  width: 62px;
  height: 62px;
  display: block;
  margin: 0 0 24px 5px;
  object-fit: contain;
}

.nav-menu {
  display: grid;
  width: 182px;
}

.nav-item {
  width: 182px;
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  align-items: center;
  min-height: 52px;
  border: 0;
  border-right: 1px solid #75ddcb;
  border-bottom: 1px solid #75ddcb;
  background: transparent;
  color: #050505;
  text-align: left;
  cursor: pointer;
}

.nav-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-item.active {
  color: #715cff;
  font-weight: 700;
}

.nav-icon-img {
  width: 34px;
  height: 34px;
  justify-self: center;
  object-fit: contain;
}

@media (max-width: 860px) {
  .sidebar {
    width: 100%;
    min-width: 0;
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
    width: 100%;
    grid-template-columns: 34px minmax(0, 1fr);
    min-height: 44px;
  }

  .nav-icon-img {
    width: 24px;
    height: 24px;
  }
}
</style>
