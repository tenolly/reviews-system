<template>
  <div class="auth container">
    <section class="card form-card">
      <h1>С возвращением</h1>
      <p class="subtitle">Войдите с помощью имени пользователя и пароля.</p>

      <form class="form" @submit.prevent="handleLogin">
        <label class="field">
          <span class="label">Имя пользователя</span>
          <input v-model="username" type="text" required placeholder="username" />
        </label>

        <label class="field">
          <span class="label">Пароль</span>
          <input v-model="password" type="password" required placeholder="••••••" />
        </label>

        <button type="submit" class="btn primary" :disabled="submitting">
          {{ submitting ? 'Входим...' : 'Войти' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <p class="switch">
        Нет аккаунта?
        <router-link to="/register">Зарегистрируйтесь</router-link>
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const { login } = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

const handleLogin = async () => {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = 'Заполните оба поля, чтобы продолжить.'
    return
  }

  submitting.value = true
  try {
    await login({ username: username.value, password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.push(redirect).catch(() => {})
  } catch (err) {
    const apiMessage = err?.response?.data?.detail || err?.response?.data?.non_field_errors?.[0]
    error.value = apiMessage || 'Не удалось выполнить вход. Проверьте данные и попробуйте снова.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth {
  display: flex;
  justify-content: center;
  padding-top: 48px;
}

.form-card {
  width: min(420px, 100%);
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 36px;
}

.subtitle {
  margin: 0;
  color: var(--color-muted);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
  color: var(--color-muted);
}

.field input {
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
}


.btn.primary {
  width: 100%;
}

.error {
  color: var(--color-error);
  margin: 0;
}

.switch {
  margin: 0;
  color: var(--color-muted);
  text-align: center;
}

.switch a {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
