<template>
  <div class="auth container">
    <section class="card form-card">
      <h1>Создайте аккаунт</h1>
      <p class="subtitle">Придумайте имя пользователя и пароль.</p>

      <form class="form" @submit.prevent="handleRegister">
        <label class="field">
          <span class="label">Имя пользователя</span>
          <input v-model="username" type="text" required placeholder="username" />
        </label>

        <label class="field">
          <span class="label">Пароль</span>
          <input v-model="password" type="password" required placeholder="8-32 символов" minlength="6" maxlength="32" />
        </label>

        <label class="field">
          <span class="label">Повторите пароль</span>
          <input v-model="repeat" type="password" required placeholder="Повторите пароль" />
        </label>

        <button type="submit" class="btn primary" :disabled="submitting">
          {{ submitting ? 'Отправляем...' : 'Зарегистрироваться' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">Аккаунт создан. Можете войти с указанными данными.</p>
      </form>

      <p class="switch">
        Уже есть аккаунт?
        <router-link to="/login">Войти</router-link>
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { register } = useAuthStore()

  const username = ref('')
const password = ref('')
const repeat = ref('')
const error = ref('')
const success = ref(false)
const submitting = ref(false)

const passwordPattern = /^[A-Za-z0-9!@#$%^&*()_+=-]{6,32}$/

const handleRegister = async () => {
  error.value = ''
  success.value = false

  if (!username.value || !password.value || !repeat.value) {
    error.value = 'Заполните все поля, чтобы продолжить.'
    return
  }

  if (password.value !== repeat.value) {
    error.value = 'Пароли не совпадают.'
    return
  }

  if (!passwordPattern.test(password.value)) {
    error.value = 'Пароль должен содержать 6-32 допустимых символа.'
    return
  }

  submitting.value = true
  try {
    await register({ username: username.value, password: password.value, password_confirm: repeat.value })
    success.value = true
    router.push({ name: 'home' }).catch(() => {})
  } catch (err) {
    const apiMessage = err?.response?.data?.detail || err?.response?.data?.non_field_errors?.[0]
    error.value = apiMessage || 'Не удалось зарегистрироваться. Попробуйте снова.'
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
  width: min(460px, 100%);
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

.success {
  color: var(--color-success);
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
