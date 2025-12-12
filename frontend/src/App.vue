<template>
  <div id="app">
    <AppHeader />
    <main class="app-main">
      <section v-if="isBanned" class="banned-overlay">
        <div class="banned-content">
          <h1>Доступ ограничен</h1>
          <p>Ваш аккаунт заблокирован. Для восстановления доступа обратитесь в поддержку.</p>
          <div class="actions">
            <button type="button" class="btn ghost" @click="handleLogout">Выйти</button>
          </div>
        </div>
      </section>
      <router-view v-else />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import { useAuthStore } from './stores/auth'

const { user, initAuth, logout } = useAuthStore()
const router = useRouter()
const isBanned = computed(() => user.value.banned)

onMounted(() => {
  void initAuth()
})

const handleLogout = async () => {
  await logout()
  router.push('/').catch(() => {})
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--app-background);
  transition: background 0.35s ease;
}

.app-main {
  flex: 1;
  padding: 32px 0 64px;
}

.banned-overlay {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 64px 16px;
  text-align: center;
}

.banned-content {
  max-width: 640px;
  width: 100%;
  padding: 48px;
  border-radius: 24px;
  background: linear-gradient(145deg, rgba(220, 38, 38, 0.12), rgba(248, 113, 113, 0.28));
  color: var(--color-error);
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 24px 60px rgba(220, 38, 38, 0.15);
}

.actions {
  display: flex;
  justify-content: center;
}

.banned-content h1 {
  margin: 0;
  font-size: 58px;
  font-weight: 800;
}

.banned-content p {
  margin: 0;
  font-size: 18px;
  color: rgba(153, 27, 27, 0.9);
}

@media (max-width: 768px) {
  .app-main {
    padding: 24px 0 48px;
  }

  .banned-overlay {
    min-height: calc(100vh - 160px);
    padding: 48px 12px;
  }

  .banned-content {
    padding: 32px;
    gap: 14px;
  }

  .banned-content h1 {
    font-size: 38px;
  }
}
</style>
