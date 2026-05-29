<script setup lang="ts">
import MenuLateral from './MenuLateral.vue'
const props = defineProps<{
  displayName: string
  username: string
  email: string
}>()

const emit = defineEmits<{
  'go-home': []
  'edit-profile': []
  logout: []
  navigate: [section: string]
}>()

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

      <div class="profile-layout">
        <div class="profile-avatar" aria-hidden="true">
          <div class="avatar-hair"></div>
          <div class="avatar-face"></div>
          <div class="avatar-beard"></div>
          <div class="avatar-body"></div>
        </div>

        <div class="profile-info">
          <h2>{{ props.displayName }}</h2>
          <p class="profile-email">{{ props.email }}</p>

          <dl class="profile-fields">
            <div>
              <dt>Nombre de usuario</dt>
              <dd>{{ props.username }}</dd>
            </div>
            <div>
              <dt>Correo electrónico</dt>
              <dd>{{ props.email }}</dd>
            </div>
          </dl>

          <div class="profile-actions">
            <button class="edit-button" type="button" @click="emit('edit-profile')">Editar perfil</button>
            <button class="logout-button" type="button" @click="emit('logout')">Cerrar sesión</button>
          </div>
        </div>
      </div>
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
  padding: 54px 74px 54px 60px;
}

.profile-content h1 {
  margin: 0 0 22px;
  font-size: clamp(2rem, 3.8vw, 2.45rem);
  line-height: 1;
}

.profile-layout {
  display: grid;
  grid-template-columns: 96px minmax(0, 540px);
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

.profile-info h2 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.35rem);
  line-height: 1;
}

.profile-email {
  margin: 12px 0 28px;
  font-size: 1rem;
}

.profile-fields {
  display: grid;
  gap: 34px;
  margin: 0;
}

.profile-fields div {
  display: grid;
  grid-template-columns: 190px minmax(0, 1fr);
  align-items: baseline;
  gap: 0;
}

.profile-fields dt {
  font-size: 1.14rem;
}

.profile-fields dd {
  min-width: 0;
  margin: 0;
  color: #715cff;
  overflow-wrap: anywhere;
  font-size: 1rem;
}

.profile-actions {
  width: min(100%, 458px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 222px));
  gap: 14px;
  margin: 52px 0 0;
}

.edit-button,
.logout-button {
  width: 100%;
  height: 30px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  cursor: pointer;
}

.edit-button {
  background: #7563f6;
}

.logout-button {
  background: #e43f4d;
}

@media (max-width: 860px) {
  .profile-frame {
    grid-template-columns: 1fr;
  }

  .profile-content {
    padding: 28px 20px 36px;
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .profile-fields div {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .profile-actions {
    width: min(100%, 460px);
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
