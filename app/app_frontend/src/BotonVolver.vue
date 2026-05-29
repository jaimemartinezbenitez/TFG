<script setup lang="ts">
const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <button class="back-button" type="button" @click="emit('click')">
    <span aria-hidden="true">‹</span>
    Volver
  </button>
</template>

<style scoped>
.back-button {
  position: fixed;
  top: 18px;
  left: 232px;
  z-index: 9999;
  min-width: 118px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 2px solid #715cff;
  border-radius: 999px;
  background: #715cff;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 3px 12px rgb(113 92 255 / 26%);
}

.back-button span {
  font-size: 1.45rem;
  line-height: 1;
}

.back-button:hover,
.back-button:focus-visible {
  border-color: #5847df;
  background: #5847df;
  color: #fff;
  outline: none;
}

@media (max-width: 860px) {
  .back-button {
    top: 14px;
    left: 16px;
  }
}
</style>
