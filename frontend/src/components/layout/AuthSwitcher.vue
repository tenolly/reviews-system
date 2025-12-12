<template>
  <aside class="auth-switcher" aria-label="Переключение профилей">
    <div class="switcher-header">Роли для теста</div>
    <div class="switcher-buttons">
      <button
        v-for="entry in profileEntries"
        :key="entry.key"
        type="button"
        class="switcher-btn"
        :class="{ active: profileKey === entry.key }"
        @click="switchProfile(entry.key)"
      >
        {{ labelMap[entry.key] ?? entry.profile.fullName }}
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const { profiles, profileKey, switchProfile } = useAuthStore()

const profileEntries = computed(() =>
  Object.entries(profiles).map(([key, profile]) => ({ key, profile }))
)

const labelMap = {
  guest: 'Гость',
  user: 'Пользователь',
  admin: 'Админ',
  banned: 'Заблокирован'
}
</script>

<style scoped>
.auth-switcher {
  position: fixed;
  right: 18px;
  bottom: 18px;
  background: rgba(15, 23, 42, 0.8);
  color: #ffffff;
  padding: 14px;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.3);
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 20;
}

.switcher-header {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.6);
}

.switcher-buttons {
  display: flex;
  gap: 8px;
}

.switcher-btn {
  background: rgba(255, 255, 255, 0.12);
  border: none;
  color: #ffffff;
  padding: 6px 10px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.switcher-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.switcher-btn.active {
  background: #ffffff;
  color: #0f172a;
}

@media (max-width: 640px) {
  .auth-switcher {
    display: none;
  }
}
</style>
