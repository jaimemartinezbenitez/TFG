<script setup lang="ts">
import { ref } from 'vue'
import MenuLateral from './MenuLateral.vue'
import type { EditProfileForm } from './types'

const props = defineProps<{
  displayName: string
  username: string
  email: string
  form: EditProfileForm
  loading: boolean
  message: string
}>()

const emit = defineEmits<{
  submit: []
  cancel: []
  'go-home': []
  logout: []
  navigate: [section: string]
}>()

const showOldPassword = ref(false)
const showNewPassword = ref(false)

function handleNavigation(section: string) {
  if (section === 'inicio') emit('go-home')
  else emit('navigate', section)
}
</script>

<template>
  <section class="profile-frame">
    <MenuLateral @navigate="handleNavigation" />

    <section class="profile-content">
      <h1>Mi perfil</h1>

      <form class="profile-layout" @submit.prevent="emit('submit')">
        <div class="profile-avatar" aria-hidden="true">
          <div class="avatar-hair"></div>
          <div class="avatar-face"></div>
          <div class="avatar-beard"></div>
          <div class="avatar-body"></div>
        </div>

        <div class="profile-info">
          <div class="profile-heading">
            <div>
              <h2>{{ props.displayName }}</h2>
              <p class="profile-email">{{ props.email }}</p>
            </div>

            <div class="profile-actions">
              <button class="confirm-button" type="submit" :disabled="props.loading">
                {{ props.loading ? 'Guardando...' : 'Confirmar cambios' }}
              </button>
              <button class="cancel-button" type="button" :disabled="props.loading" @click="emit('cancel')">
                Cancelar
              </button>
            </div>
          </div>

          <div class="edit-fields">
            <label for="currentUsername">Nombre de usuario</label>
            <span id="currentUsername" class="current-value">{{ props.username }}</span>

            <label for="newUsername">Nuevo nombre de usuario</label>
            <input
              id="newUsername"
              v-model.trim="props.form.username"
              autocomplete="username"
              placeholder="Opcional"
            />

            <label for="currentEmail">Correo electrónico</label>
            <span id="currentEmail" class="current-value">{{ props.email }}</span>

            <label for="newEmail">Nuevo correo electrónico</label>
            <input
              id="newEmail"
              v-model.trim="props.form.email"
              type="email"
              autocomplete="email"
              placeholder="Opcional"
            />

            <label for="oldPassword">Contraseña actual</label>
            <div class="password-input">
              <input
                id="oldPassword"
                v-model="props.form.oldPassword"
                :type="showOldPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Opcional"
              />
              <button
                class="visibility-button"
                type="button"
                :aria-label="showOldPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="showOldPassword = !showOldPassword"
              >
                <span class="eye-icon" :class="{ hidden: !showOldPassword }" aria-hidden="true"></span>
              </button>
            </div>

            <label for="newPassword">Nueva contraseña</label>
            <div class="password-input">
              <input
                id="newPassword"
                v-model="props.form.password"
                :type="showNewPassword ? 'text' : 'password'"
                maxlength="12"
                autocomplete="new-password"
                placeholder="Opcional"
              />
              <button
                class="visibility-button"
                type="button"
                :aria-label="showNewPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="showNewPassword = !showNewPassword"
              >
                <span class="eye-icon" :class="{ hidden: !showNewPassword }" aria-hidden="true"></span>
              </button>
            </div>
          </div>

          <p v-if="props.message" class="form-message">{{ props.message }}</p>
        </div>
      </form>
    </section>
  </section>
</template>

<style scoped>
.profile-frame {
  min-height: calc(100vh - 8px);
  margin: 3px;
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  border: 2px solid #0d0d0d;
  border-radius: 22px;
  background: #fff;
  overflow: hidden;
}

.profile-content {
  min-width: 0;
  padding: 54px 14px 54px 60px;
}

.profile-content h1 {
  margin: 0 0 22px;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.profile-layout {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.profile-avatar {
  position: relative;
  width: 96px;
  height: 92px;
  overflow: hidden;
  border: 1.5px solid #101010;
  border-radius: 24px;
  background: #fff;
}

.avatar-hair {
  position: absolute;
  top: 7px;
  left: 25px;
  width: 45px;
  height: 42px;
  border-radius: 20px 20px 14px 14px;
  background: #9b4b2b;
}

.avatar-face {
  position: absolute;
  top: 16px;
  left: 29px;
  width: 38px;
  height: 42px;
  border-radius: 16px 16px 20px 20px;
  background: #f1b77e;
}

.avatar-beard {
  position: absolute;
  top: 44px;
  left: 31px;
  width: 34px;
  height: 27px;
  border-radius: 4px 4px 18px 18px;
  background: #9b4b2b;
}

.avatar-body {
  position: absolute;
  right: -7px;
  bottom: -10px;
  left: -7px;
  height: 33px;
  border-radius: 50% 50% 0 0;
  background: #0f2a3f;
}

.profile-info {
  min-width: 0;
}

.profile-heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 20px;
  align-items: start;
}

.profile-info h2 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.35rem);
  line-height: 1;
}

.profile-email {
  margin: 12px 0 26px;
  font-size: 1rem;
}

.profile-actions {
  display: grid;
  grid-template-columns: repeat(2, 158px);
  gap: 12px;
  align-items: center;
  padding-top: 32px;
}

.confirm-button,
.cancel-button {
  height: 30px;
  border-radius: 999px;
  cursor: pointer;
}

.confirm-button {
  width: 158px;
  border: 0;
  color: #fff;
  background: #7563f6;
}

.cancel-button {
  width: 158px;
  border: 1.5px solid #101010;
  color: #101010;
  background: #fff;
}

.confirm-button:disabled,
.cancel-button:disabled {
  cursor: progress;
  opacity: 0.7;
}

.edit-fields {
  display: grid;
  grid-template-columns: 244px minmax(0, 240px);
  gap: 26px 0;
  align-items: center;
}

.edit-fields label {
  font-size: 1.14rem;
}

.current-value {
  min-width: 0;
  color: #715cff;
  overflow-wrap: anywhere;
  font-size: 1rem;
}

.edit-fields input {
  width: 100%;
  height: 30px;
  border: 2px solid #7161ff;
  border-radius: 8px;
  padding: 0 12px;
  outline: none;
  background: #fff;
  font-style: italic;
}

.edit-fields input:focus {
  box-shadow: 0 0 0 3px rgb(113 97 255 / 16%);
}

.password-input {
  position: relative;
}

.password-input input {
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
  max-width: 520px;
  margin: 20px 0 0;
  color: #e5333f;
  font-size: 0.95rem;
}

@media (max-width: 940px) {
  .profile-heading {
    display: grid;
  }

  .profile-actions {
    width: min(100%, 328px);
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding-top: 0;
  }

  .confirm-button,
  .cancel-button {
    width: 100%;
  }
}

@media (max-width: 860px) {
  .profile-frame {
    grid-template-columns: 1fr;
  }

  .profile-content {
    padding: 28px 20px 36px;
  }

  .profile-layout,
  .edit-fields {
    grid-template-columns: 1fr;
  }

  .edit-fields {
    gap: 8px;
  }

  .edit-fields input,
  .password-input {
    width: min(100%, 320px);
  }
}
</style>
