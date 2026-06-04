<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaRecuperarContrasena.vue"
Descripcion: Representa el flujo para recuperar la contraseña mediante token.
-->

<script setup lang="ts">
import { ref } from 'vue'
import type { AuthMode, PasswordResetForm } from './types'

const props = defineProps<{
  form: PasswordResetForm
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  'request-reset': []
  'confirm-reset': []
  'switch-mode': [mode: AuthMode]
}>()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
</script>

<template>
  <section class="reset-screen">
    <div class="reset-frame">
      <img class="brand-logo" src="/logo.png" alt="ConcentraPlus" />

      <div class="reset-panel">
        <header>
          <h1>Recuperar contraseña</h1>
          <p>Genera un token de recuperación y escribe tu nueva contraseña.</p>
        </header>

        <form class="reset-form request-form" @submit.prevent="emit('request-reset')">
          <h2>Generar token</h2>
          <label for="resetEmail">Correo de la cuenta</label>
          <input
            id="resetEmail"
            v-model.trim="props.form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="correo@ejemplo.com"
          />
          <button class="secondary-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Generando...' : 'Generar token' }}
          </button>
        </form>

        <form class="reset-form confirm-form" @submit.prevent="emit('confirm-reset')">
          <h2>Confirmar cambio</h2>
          <label for="resetToken">Token recibido</label>
          <input id="resetToken" v-model.trim="props.form.token" required autocomplete="one-time-code" />

          <label for="resetPassword">Nueva contraseña</label>
          <div class="password-input">
            <input
              id="resetPassword"
              v-model="props.form.password"
              required
              maxlength="12"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
            />
            <button
              class="visibility-button"
              type="button"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="showPassword = !showPassword"
            >
              <span class="eye-icon" :class="{ hidden: !showPassword }" aria-hidden="true"></span>
            </button>
          </div>

          <label for="resetConfirmPassword">Confirmar contraseña</label>
          <div class="password-input">
            <input
              id="resetConfirmPassword"
              v-model="props.form.confirmPassword"
              required
              maxlength="12"
              :type="showConfirmPassword ? 'text' : 'password'"
              autocomplete="new-password"
            />
            <button
              class="visibility-button"
              type="button"
              :aria-label="showConfirmPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <span class="eye-icon" :class="{ hidden: !showConfirmPassword }" aria-hidden="true"></span>
            </button>
          </div>

          <p v-if="props.message" class="form-message">{{ props.message }}</p>

          <button class="submit-button" type="submit" :disabled="props.loading">
            {{ props.loading ? 'Actualizando...' : 'Cambiar contraseña' }}
          </button>
        </form>

        <p class="switch-copy">
          <a href="#" @click.prevent="emit('switch-mode', 'login')">Volver al inicio de sesión</a>
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.reset-screen {
  min-height: 100vh;
  padding: 3px;
  background: #fbfbfc;
}

.reset-frame {
  min-height: calc(100vh - 6px);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid #101010;
  border-radius: 22px;
  background: #fff;
  padding: clamp(20px, 4vh, 32px) 24px 56px;
}

.brand-logo {
  width: min(454px, 72vw);
  max-height: 124px;
  display: block;
  object-fit: contain;
}

.reset-panel {
  width: min(100%, 760px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px 28px;
  margin-top: 12px;
  border: 2px solid #715cff;
  border-radius: 8px;
  padding: clamp(22px, 4vw, 34px);
}

header,
.switch-copy {
  grid-column: 1 / -1;
  text-align: center;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1;
}

header p {
  margin: 14px 0 0;
  font-size: 1.08rem;
}

.reset-form {
  display: grid;
  align-content: start;
  gap: 10px;
}

h2 {
  margin: 0 0 4px;
  font-size: 1.24rem;
}

label {
  font-size: 1rem;
}

input {
  width: 100%;
  height: 34px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 0 12px;
  outline: none;
  background: #fff;
}

input:focus {
  box-shadow: 0 0 0 3px rgb(113 97 255 / 16%);
}

.password-input {
  position: relative;
}

.password-input input {
  padding-right: 38px;
}

.visibility-button {
  position: absolute;
  top: 50%;
  right: 8px;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border: 0;
  background: transparent;
  padding: 0;
  transform: translateY(-50%);
  cursor: pointer;
}

.eye-icon {
  position: relative;
  width: 18px;
  height: 11px;
  border: 1.7px solid #111;
  border-radius: 50%;
}

.eye-icon::before {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #111;
  content: "";
  transform: translate(-50%, -50%);
}

.eye-icon.hidden::after {
  position: absolute;
  top: 4px;
  left: -3px;
  width: 24px;
  height: 2px;
  border-radius: 999px;
  background: #111;
  content: "";
  transform: rotate(-35deg);
}

.secondary-button,
.submit-button {
  height: 34px;
  margin-top: 8px;
  border-radius: 999px;
  cursor: pointer;
}

.secondary-button {
  border: 1.5px solid #101010;
  color: #101010;
  background: #fff;
}

.submit-button {
  border: 0;
  color: #fff;
  background: #7563f6;
}

.secondary-button:disabled,
.submit-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

.form-message {
  margin: 0;
  color: #e5333f;
  text-align: center;
  font-size: 0.92rem;
}

.switch-copy {
  margin: 0;
}

.switch-copy a {
  color: #7563f6;
  text-decoration: none;
}

@media (max-width: 760px) {
  .reset-panel {
    grid-template-columns: 1fr;
  }
}
</style>
