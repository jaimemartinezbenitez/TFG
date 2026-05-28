<script setup lang="ts">
import { ref } from 'vue'
import type { AuthMode, RegisterForm } from './types'

const props = defineProps<{
  registerForm: RegisterForm
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  'submit-register': []
  'switch-mode': [mode: AuthMode]
}>()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
</script>

<template>
  <section class="register-screen">
    <div class="register-frame">
      <img class="brand-logo" src="/logo.png" alt="ConcentraPlus" />

      <form class="register-form" @submit.prevent="emit('submit-register')">
        <h1>Crear cuenta</h1>

        <div class="field">
          <label for="username">Nombre de usuario</label>
          <input id="username" v-model.trim="props.registerForm.username" required autocomplete="username" />
        </div>

        <div class="field">
          <label for="email">Correo electrónico</label>
          <input
            id="email"
            v-model.trim="props.registerForm.email"
            required
            type="email"
            autocomplete="email"
          />
        </div>

        <div class="field">
          <label for="password">Contraseña</label>
          <div class="password-input">
            <input
              id="password"
              v-model="props.registerForm.password"
              required
              :type="showPassword ? 'text' : 'password'"
              maxlength="12"
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
        </div>

        <div class="field">
          <label for="confirmPassword">Confirmar contraseña</label>
          <div class="password-input">
            <input
              id="confirmPassword"
              v-model="props.registerForm.confirmPassword"
              required
              :type="showConfirmPassword ? 'text' : 'password'"
              maxlength="12"
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
        </div>

        <p v-if="props.message" class="form-message">{{ props.message }}</p>

        <button class="submit-button" type="submit" :disabled="props.loading">
          {{ props.loading ? 'Registrando...' : 'Registrarse' }}
        </button>
        <p class="switch-copy">
          ¿Ya tienes una cuenta?
          <a href="#" @click.prevent="emit('switch-mode', 'login')">Inicia sesión</a>
        </p>
      </form>
    </div>
  </section>
</template>

<style scoped>
.register-screen {
  min-height: 100vh;
  padding: 3px;
  background: #fbfbfc;
}

.register-frame {
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

.register-form {
  width: min(100%, 360px);
  display: grid;
  justify-items: center;
  margin-top: 8px;
}

.register-form h1 {
  margin: 0 0 18px;
  text-align: center;
  font-size: clamp(2rem, 4vw, 2.35rem);
  line-height: 1.1;
}

.field {
  width: 100%;
  display: grid;
  justify-items: start;
  gap: 9px;
  margin-bottom: 14px;
}

.field label {
  font-size: 1.05rem;
}

.field > input,
.password-input input {
  width: 300px;
  max-width: 100%;
  height: 30px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 0 12px;
  outline: none;
  background: #fff;
}

.field > input:focus,
.password-input input:focus {
  box-shadow: 0 0 0 3px rgb(113 97 255 / 16%);
}

.password-input {
  position: relative;
  width: 300px;
  max-width: 100%;
}

.password-input input {
  width: 100%;
  padding-right: 40px;
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

.form-message {
  width: 100%;
  margin: 0 0 12px;
  color: #e5333f;
  text-align: center;
  font-size: 0.9rem;
}

.submit-button {
  width: 222px;
  max-width: 100%;
  height: 30px;
  margin-top: 8px;
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

.switch-copy a {
  color: #7563f6;
  text-decoration: none;
}

@media (max-width: 620px) {
  .register-frame {
    justify-content: center;
    padding-inline: 18px;
  }

  .field > input,
  .password-input {
    width: 100%;
  }
}
</style>
