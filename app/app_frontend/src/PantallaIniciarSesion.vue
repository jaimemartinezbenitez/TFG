<!--
Autor: Jaime Martínez Benítez
TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
Archivo: "PantallaIniciarSesion.vue"
Descripcion: Representa el formulario de inicio de sesión.
-->

<script setup lang="ts">
import { ref } from 'vue'
import type { AuthMode, LoginForm } from './types'

const props = defineProps<{
  loginForm: LoginForm
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  'submit-login': []
  'switch-mode': [mode: AuthMode]
}>()

const showPassword = ref(false)
</script>

<template>
  <section class="login-screen">
    <div class="login-frame">
      <img class="brand-logo" src="/logo.png" alt="ConcentraPlus" />

      <form class="login-form" @submit.prevent="emit('submit-login')">
        <h1>Bienvenido de nuevo!  <span aria-hidden="true">👋</span></h1>
        <p class="intro-copy">Inicia sesión para continuar</p>

        <div class="field">
          <label for="loginUser">Correo electrónico o usuario</label>
          <input id="loginUser" v-model.trim="props.loginForm.username" required autocomplete="username" />
        </div>

        <div class="field">
          <label for="loginPassword">Contraseña</label>
          <div class="password-row">
            <div class="password-input">
              <input
                id="loginPassword"
                v-model="props.loginForm.password"
                required
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
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
            <a class="forgot-link" href="#" @click.prevent="emit('switch-mode', 'password-reset')">
              ¿Olvidaste la contraseña?
            </a>
          </div>
        </div>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <button class="submit-button" type="submit" :disabled="props.loading">
          {{ props.loading ? 'Entrando...' : 'Iniciar Sesión' }}
        </button>
        <p class="switch-copy">
          ¿No tienes una cuenta?
          <a href="#" @click.prevent="emit('switch-mode', 'register')">Regístrate</a>
        </p>
      </form>
    </div>
  </section>
</template>

<style scoped>
.login-screen {
  min-height: 100vh;
  padding: 3px;
  background: #fbfbfc;
}

.login-frame {
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

.login-form {
  width: min(100%, 360px);
  display: grid;
  justify-items: center;
  margin-top: 10px;
}

.login-form h1 {
  max-width: 100%;
  margin: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  font-size: clamp(1.8rem, 3.6vw, 2.35rem);
  line-height: 1.1;
  white-space: nowrap;
}

.login-form h1 span {
  flex: 0 0 auto;
  line-height: 1;
}

.intro-copy {
  margin: 14px 0 18px;
  text-align: center;
  font-size: 1.18rem;
}

.field {
  width: 100%;
  display: grid;
  gap: 10px;
  margin-bottom: 18px;
}

.field label {
  font-size: 1.05rem;
}

.field > input,
.password-input input {
  height: 30px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 0 12px;
  outline: none;
  background: #fff;
}

.field > input {
  width: 300px;
  max-width: 100%;
}

.field > input:focus,
.password-input input:focus {
  box-shadow: 0 0 0 3px rgb(113 97 255 / 16%);
}

.password-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.password-input {
  position: relative;
  width: 220px;
  flex: 0 0 auto;
}

.password-input input {
  width: 100%;
  padding-right: 36px;
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

.forgot-link,
.switch-copy a {
  color: #7563f6;
  text-decoration: none;
}

.forgot-link {
  font-size: 0.94rem;
  white-space: nowrap;
}

.form-message {
  width: 100%;
  margin: -2px 0 12px;
  color: #e5333f;
  text-align: center;
  font-size: 0.9rem;
}

.submit-button {
  width: 222px;
  max-width: 100%;
  height: 30px;
  margin-top: 10px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #7563f6;
  cursor: pointer;
}

.submit-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

.switch-copy {
  margin: 18px 0 0;
  text-align: center;
  font-size: 0.95rem;
}

@media (max-width: 620px) {
  .login-frame {
    justify-content: center;
    padding-inline: 18px;
  }

  .login-form h1 {
    gap: 6px;
    font-size: clamp(1.45rem, 8vw, 1.85rem);
  }

  .password-row {
    display: grid;
    gap: 8px;
  }

  .password-input,
  .field > input {
    width: 100%;
  }
}
</style>
