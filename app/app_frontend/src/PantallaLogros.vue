<script setup lang="ts">
import { computed, ref } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { Achievement } from './types'

const props = defineProps<{
  initials: string
  achievements: Achievement[]
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  navigate: [section: string]
  'open-profile': []
}>()

type AchievementPeriod = 'general' | 'weekly' | 'monthly' | 'yearly'
type AchievementTone =
  | 'green'
  | 'purple'
  | 'orange'
  | 'blue'
  | 'teal'
  | 'rose'
  | 'gold'
  | 'indigo'
  | 'cyan'
  | 'lime'
  | 'red'
  | 'slate'

type AchievementCard = {
  name: string
  title: string
  description: string
  symbol: string
  period: AchievementPeriod
  tone: AchievementTone
}

const selectedPeriod = ref<AchievementPeriod>('general')

const periods: Array<{ id: AchievementPeriod; label: string }> = [
  { id: 'general', label: 'Generales' },
  { id: 'weekly', label: 'Semanales' },
  { id: 'monthly', label: 'Mensuales' },
  { id: 'yearly', label: 'Anuales' },
]

const catalog: AchievementCard[] = [
  {
    name: 'Primeros pasos',
    title: 'Primeros pasos',
    description: 'Completa tu primera tarea',
    symbol: '★',
    period: 'general',
    tone: 'green',
  },
  {
    name: 'Enfoque total',
    title: 'Enfoque total',
    description: 'Completa 10 sesiones Pomodoro',
    symbol: '◴',
    period: 'general',
    tone: 'purple',
  },
  {
    name: 'Constante',
    title: 'Constante',
    description: '7 dias seguidos activo',
    symbol: '♛',
    period: 'general',
    tone: 'orange',
  },
  {
    name: 'Productivo',
    title: 'Productivo',
    description: 'Completa 50 tareas',
    symbol: '↗',
    period: 'general',
    tone: 'blue',
  },
  {
    name: 'Madrugador',
    title: 'Madrugador',
    description: 'Completa tareas antes de las 8am',
    symbol: '☼',
    period: 'general',
    tone: 'gold',
  },
  {
    name: 'Maratonista',
    title: 'Maratonista',
    description: '4 sesiones Pomodoro en un dia',
    symbol: '◆',
    period: 'general',
    tone: 'rose',
  },
  {
    name: 'Imparable',
    title: 'Imparable',
    description: '30 dias seguidos activo',
    symbol: '∞',
    period: 'general',
    tone: 'indigo',
  },
  {
    name: 'Experto',
    title: 'Experto',
    description: 'Completa 100 tareas',
    symbol: '✦',
    period: 'general',
    tone: 'cyan',
  },
  {
    name: 'Semana en marcha',
    title: 'Semana en marcha',
    description: 'Completa una tarea esta semana',
    symbol: 'Ⅰ',
    period: 'weekly',
    tone: 'green',
  },
  {
    name: 'Sprint semanal',
    title: 'Sprint semanal',
    description: 'Completa 5 tareas esta semana',
    symbol: 'Ⅴ',
    period: 'weekly',
    tone: 'teal',
  },
  {
    name: 'Semana enfocada',
    title: 'Semana enfocada',
    description: 'Acumula 3 horas de enfoque esta semana',
    symbol: '⌁',
    period: 'weekly',
    tone: 'purple',
  },
  {
    name: 'Ritmo semanal',
    title: 'Ritmo semanal',
    description: 'Registra sesiones en 5 dias de la semana',
    symbol: '▣',
    period: 'weekly',
    tone: 'orange',
  },
  {
    name: 'Mes activo',
    title: 'Mes activo',
    description: 'Completa 5 tareas este mes',
    symbol: '◇',
    period: 'monthly',
    tone: 'blue',
  },
  {
    name: 'Mes productivo',
    title: 'Mes productivo',
    description: 'Completa 20 tareas este mes',
    symbol: '◈',
    period: 'monthly',
    tone: 'lime',
  },
  {
    name: 'Mes de enfoque',
    title: 'Mes de enfoque',
    description: 'Acumula 15 horas de enfoque este mes',
    symbol: '◉',
    period: 'monthly',
    tone: 'indigo',
  },
  {
    name: 'Constancia mensual',
    title: 'Constancia mensual',
    description: 'Registra sesiones en 15 dias del mes',
    symbol: '▰',
    period: 'monthly',
    tone: 'gold',
  },
  {
    name: 'Ano constante',
    title: 'Año constante',
    description: 'Registra actividad en 60 dias del año',
    symbol: '✧',
    period: 'yearly',
    tone: 'cyan',
  },
  {
    name: 'Ano productivo',
    title: 'Año productivo',
    description: 'Completa 150 tareas este año',
    symbol: '⬡',
    period: 'yearly',
    tone: 'green',
  },
  {
    name: 'Ano de enfoque',
    title: 'Año de enfoque',
    description: 'Acumula 100 horas de enfoque este año',
    symbol: '✺',
    period: 'yearly',
    tone: 'purple',
  },
  {
    name: 'Maestria anual',
    title: 'Maestría anual',
    description: 'Completa 300 tareas y 200 horas de enfoque',
    symbol: '♢',
    period: 'yearly',
    tone: 'red',
  },
]

const unlockedByName = computed(() => new Map(props.achievements.map((achievement) => [achievement.name, achievement])))
const filteredCatalog = computed(() => catalog.filter((achievement) => achievement.period === selectedPeriod.value))
const unlockedCount = computed(() => catalog.filter((achievement) => unlockedByName.value.has(achievement.name)).length)
const periodUnlockedCount = computed(() =>
  filteredCatalog.value.filter((achievement) => unlockedByName.value.has(achievement.name)).length,
)
const currentPeriodLabel = computed(() => periods.find((period) => period.id === selectedPeriod.value)?.label || 'Logros')

function isUnlocked(achievement: AchievementCard) {
  return unlockedByName.value.has(achievement.name)
}

function achievedDate(achievement: AchievementCard) {
  const item = unlockedByName.value.get(achievement.name)
  if (!item) return ''
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }).format(
    new Date(item.achieved_at),
  )
}
</script>

<template>
  <section class="achievements-frame">
    <MenuLateral active="logros" @navigate="emit('navigate', $event)" />

    <section class="achievements-content">
      <button class="avatar-button" type="button" title="Ver perfil" @click="emit('open-profile')">
        <span>{{ props.initials }}</span>
      </button>

      <header class="achievements-header">
        <div>
          <h1>Logros</h1>
          <p>{{ unlockedCount }} de {{ catalog.length }} desbloqueados</p>
        </div>

        <div class="period-summary">
          <strong>{{ periodUnlockedCount }}/{{ filteredCatalog.length }}</strong>
          <span>{{ currentPeriodLabel }}</span>
        </div>
      </header>

      <nav class="period-tabs" aria-label="Categorias de logros">
        <button
          v-for="period in periods"
          :key="period.id"
          type="button"
          :class="{ active: selectedPeriod === period.id }"
          @click="selectedPeriod = period.id"
        >
          {{ period.label }}
        </button>
      </nav>

      <p v-if="props.message" class="screen-message">{{ props.message }}</p>
      <p v-else-if="props.loading" class="loading-copy">Cargando logros...</p>

      <div class="achievements-grid" aria-label="Listado de logros">
        <article
          v-for="achievement in filteredCatalog"
          :key="achievement.name"
          class="achievement-card"
          :class="[`tone-${achievement.tone}`, { locked: !isUnlocked(achievement) }]"
        >
          <div class="badge" aria-hidden="true">
            <span>{{ achievement.symbol }}</span>
          </div>

          <h2>{{ achievement.title }}</h2>
          <p>{{ achievement.description }}</p>

          <strong v-if="isUnlocked(achievement)" class="unlocked-mark">✓</strong>
          <span v-else class="locked-mark">Bloqueado</span>
          <small v-if="isUnlocked(achievement)">Desbloqueado el {{ achievedDate(achievement) }}</small>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.achievements-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.achievements-content {
  position: relative;
  min-width: 0;
  min-height: calc(100vh - 12px);
  padding: 92px 54px 74px 34px;
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

.achievements-header,
.period-tabs,
.achievements-grid,
.screen-message,
.loading-copy {
  width: min(100%, 980px);
  margin-inline: auto;
}

.achievements-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 24px;
}

h1 {
  margin: 0;
  font-size: clamp(3rem, 5vw, 4rem);
  line-height: 1;
}

.achievements-header p {
  margin: 10px 0 0;
  color: #5d6170;
  font-size: 1.05rem;
}

.period-summary {
  min-width: 150px;
  display: grid;
  justify-items: center;
  gap: 4px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: 12px 18px;
  color: #715cff;
}

.period-summary strong {
  font-size: 2rem;
  line-height: 1;
}

.period-summary span {
  font-weight: 800;
}

.period-tabs {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.period-tabs button {
  min-width: 130px;
  height: 36px;
  border: 2px solid #715cff;
  border-radius: 999px;
  color: #715cff;
  background: #fff;
  font-weight: 800;
  cursor: pointer;
}

.period-tabs button.active {
  color: #fff;
  background: #715cff;
}

.screen-message {
  color: #e5333f;
}

.loading-copy {
  color: #5d6170;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 22px;
  margin-top: 28px;
}

.achievement-card {
  min-height: 244px;
  display: grid;
  justify-items: center;
  align-content: start;
  gap: 12px;
  border: 1px solid #f0f0f2;
  border-radius: 12px;
  padding: 24px 16px 18px;
  color: #0d1430;
  text-align: center;
  box-shadow: 0 7px 20px rgb(15 20 48 / 7%);
}

.achievement-card.locked {
  color: #3b3f4f;
  background: #fff;
  opacity: 0.66;
}

.badge {
  width: 72px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border: 2px solid currentColor;
  font-size: 2rem;
  font-weight: 900;
  clip-path: polygon(50% 0, 92% 24%, 92% 74%, 50% 100%, 8% 74%, 8% 24%);
  background: color-mix(in srgb, currentColor 14%, #fff);
}

.tone-green {
  color: #159947;
}

.tone-purple {
  color: #715cff;
}

.tone-orange {
  color: #f19b24;
}

.tone-blue {
  color: #2b87d9;
}

.tone-teal {
  color: #009b84;
}

.tone-rose {
  color: #e8507a;
}

.tone-gold {
  color: #c89200;
}

.tone-indigo {
  color: #4f46e5;
}

.tone-cyan {
  color: #008bb5;
}

.tone-lime {
  color: #61a80b;
}

.tone-red {
  color: #e5333f;
}

.tone-slate {
  color: #64748b;
}

.achievement-card h2 {
  margin: 4px 0 0;
  color: #0d1430;
  font-size: 1.05rem;
}

.achievement-card p {
  min-height: 44px;
  margin: 0;
  color: #222841;
  font-size: 0.9rem;
  line-height: 1.35;
}

.achievement-card.locked p {
  color: #5f6576;
}

.unlocked-mark {
  width: 30px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #18823b;
  background: #e6f8e9;
  font-size: 1.1rem;
}

.locked-mark {
  border-radius: 999px;
  padding: 7px 14px;
  color: #7f8494;
  background: #eef0f6;
  font-size: 0.78rem;
  font-weight: 800;
}

.achievement-card small {
  color: #6c7182;
  font-size: 0.75rem;
}

@media (max-width: 1120px) {
  .achievements-grid {
    grid-template-columns: repeat(2, minmax(160px, 1fr));
  }
}

@media (max-width: 860px) {
  .achievements-frame {
    grid-template-columns: 1fr;
  }

  .achievements-content {
    padding: 82px 20px 48px;
  }

  .achievements-header {
    align-items: start;
    flex-direction: column;
  }
}

@media (max-width: 560px) {
  .period-tabs button {
    width: 100%;
  }

  .achievements-grid {
    grid-template-columns: 1fr;
  }
}
</style>
