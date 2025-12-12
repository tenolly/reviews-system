<template>
  <header class="app-header">
    <div class="container header-inner">
      <router-link class="brand" to="/">
        <span class="brand-icon">RS</span>
        <span class="brand-text">Система отзывов</span>
      </router-link>

      <nav class="nav-links" aria-label="Основная навигация">
        <router-link
          v-for="link in visibleLinks"
          :key="link.to"
          :to="link.to"
          class="nav-link"
          :class="{ active: isLinkActive(link) }"
        >
          {{ link.label }}
        </router-link>
      </nav>

      <div class="auth-block">
        <button
          class="theme-toggle"
          type="button"
          :aria-label="themeToggleLabel"
          :title="themeToggleLabel"
          @click="toggleTheme"
        >
          <span class="theme-icon" aria-hidden="true">{{ themeIcon }}</span>
        </button>
        <span class="user-chip" :class="{ banned: isBanned }">
          <span class="avatar">
            <img v-if="userAvatar" :src="userAvatar" :alt="user.fullName" />
            <span v-else class="avatar-fallback">{{ userInitials }}</span>
          </span>
          <span class="user-name">{{ user.fullName }}</span>
        </span>

        <div class="auth-actions">
          <router-link v-if="!isAuthenticated && !isBanned" class="btn ghost" to="/login">Войти</router-link>
          <router-link v-if="!isAuthenticated && !isBanned" class="btn primary" to="/register">Регистрация</router-link>
          <button v-if="isAuthenticated" class="btn ghost" type="button" @click="handleLogout">Выйти</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated, isAdmin, logout } = useAuthStore()

const THEME_STORAGE_KEY = 'reviews-theme'
const theme = ref('light')
const userSelectedTheme = ref(false)
let mediaQuery = null

const applyTheme = (value) => {
  if (typeof document === 'undefined') {
    return
  }
  document.documentElement.setAttribute('data-theme', value)
}

const resolveInitialTheme = () => {
  if (typeof window === 'undefined') {
    return 'light'
  }
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  if (stored === 'dark' || stored === 'light') {
    userSelectedTheme.value = true
    return stored
  }
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const handleSystemThemeChange = (event) => {
  if (userSelectedTheme.value) {
    return
  }
  theme.value = event.matches ? 'dark' : 'light'
}

onMounted(() => {
  theme.value = resolveInitialTheme()
  applyTheme(theme.value)

  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handleSystemThemeChange)
    } else if (typeof mediaQuery.addListener === 'function') {
      mediaQuery.addListener(handleSystemThemeChange)
    }
  }
})

onBeforeUnmount(() => {
  if (!mediaQuery) {
    return
  }
  if (typeof mediaQuery.removeEventListener === 'function') {
    mediaQuery.removeEventListener('change', handleSystemThemeChange)
  } else if (typeof mediaQuery.removeListener === 'function') {
    mediaQuery.removeListener(handleSystemThemeChange)
  }
})

watch(
  theme,
  (value) => {
    applyTheme(value)
    if (typeof window === 'undefined') {
      return
    }
    if (userSelectedTheme.value) {
      window.localStorage.setItem(THEME_STORAGE_KEY, value)
    } else {
      window.localStorage.removeItem(THEME_STORAGE_KEY)
    }
  },
  { immediate: false }
)

const toggleTheme = () => {
  userSelectedTheme.value = true
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

const themeIcon = computed(() => (theme.value === 'dark' ? '🌙' : '🌞'))
const themeToggleLabel = computed(() =>
  theme.value === 'dark' ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'
)

const isBanned = computed(() => user.value.banned)
const userAvatar = computed(() => user.value.avatar ?? '')

const navConfig = [
  { label: 'Главная', to: '/' },
  { label: 'Поиск', to: '/search' },
  { label: 'Отзывы', to: '/reviews' },
  { label: 'Оценивание', to: '/rate', requiresAuth: true },
  { label: 'Панель администратора', to: '/dashboard', requiresAdmin: true }
]

const visibleLinks = computed(() => {
  if (isBanned.value) {
    return navConfig.filter((link) => link.to === '/')
  }

  return navConfig.filter((link) => {
    if (link.requiresAdmin) {
      return isAdmin.value
    }

    if (link.requiresAuth) {
      return isAuthenticated.value
    }

    return true
  })
})

const isLinkActive = (link) => {
  if (link.to === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(link.to)
}

const userInitials = computed(() => {
  const parts = user.value.fullName.split(' ')
  const first = parts[0]?.[0] ?? 'U'
  const last = parts[1]?.[0] ?? parts[0]?.[1] ?? 'S'
  return (first + last).toUpperCase()
})

const handleLogout = async () => {
  await logout()
  router.push('/').catch(() => {})
}
</script>

<style scoped>
.app-header {
  backdrop-filter: blur(16px);
  background: var(--color-header);
  border-bottom: 1px solid var(--color-header-border);
  position: sticky;
  top: 0;
  z-index: 10;
  transition: background 0.25s ease, border-color 0.25s ease;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 18px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  color: var(--color-text);
  transition: color 0.25s ease;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 1px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.nav-link {
  padding: 8px 12px;
  border-radius: 999px;
  font-weight: 600;
  color: var(--color-muted);
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
  background-color: var(--nav-hover-bg);
  color: var(--color-primary);
}

.auth-block {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid transparent;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1),
    box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1),
    background-color 0.3s ease, border-color 0.3s ease;
}

.theme-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.2);
  background: rgba(59, 130, 246, 0.22);
}

.theme-toggle:focus-visible {
  outline: 3px solid rgba(59, 130, 246, 0.45);
  outline-offset: 3px;
}

.theme-icon {
  font-size: 18px;
  line-height: 1;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 12px;
  background-color: var(--chip-bg);
  border: 1px solid var(--chip-border);
  transition: background-color 0.25s ease, border-color 0.25s ease;
}

.user-chip.banned {
  border-color: rgba(220, 38, 38, 0.4);
  background-color: var(--chip-bg-banned);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-primary);
  display: grid;
  place-items: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-fallback {
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.auth-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}



.auth-actions .btn {
  padding: 8px 16px;
}

@media (max-width: 900px) {
  .nav-links {
    display: none;
  }
}

@media (max-width: 600px) {
  .header-inner {
    flex-wrap: wrap;
  }

  .auth-block {
    width: 100%;
    justify-content: space-between;
  }
}

:global([data-theme='dark']) .theme-toggle {
  background: rgba(96, 165, 250, 0.14);
  color: #f8fafc;
  border-color: rgba(96, 165, 250, 0.28);
}

:global([data-theme='dark']) .theme-toggle:hover {
  background: rgba(96, 165, 250, 0.26);
  box-shadow: 0 12px 28px rgba(2, 6, 23, 0.5);
}

:global([data-theme='dark']) .nav-link:hover,
:global([data-theme='dark']) .nav-link.active {
  color: var(--color-primary-light);
}

:global([data-theme='dark']) .user-chip.banned {
  border-color: rgba(248, 113, 113, 0.4);
}
</style>
