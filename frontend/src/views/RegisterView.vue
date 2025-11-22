<template>
  <div class="auth container">
    <section class="card form-card">
      <h1>Создайте аккаунт</h1>
      <p class="subtitle">Используйте корпоративную почту и подтвердите пароль.</p>

      <form class="form" @submit.prevent="handleRegister">
        <label class="field">
          <span class="label">Электронная почта</span>
          <input v-model="email" type="email" required placeholder="user@example.com" />
        </label>

        <label class="field">
          <span class="label">Пароль</span>
          <input v-model="password" type="password" required placeholder="6-32 символов" minlength="6" maxlength="32" />
        </label>

        <label class="field">
          <span class="label">Повторите пароль</span>
          <input v-model="repeat" type="password" required placeholder="Повторите пароль" />
        </label>

        <button type="submit" class="btn primary">Зарегистрироваться</button>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">Ссылка для подтверждения отправлена на вашу почту (мок-данные).</p>
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
import { loginAs } from '../stores/mockAuth'

const router = useRouter()

const email = ref('')
const password = ref('')
const repeat = ref('')
const error = ref('')
const success = ref(false)

const passwordPattern = /^[A-Za-z0-9!@#$%^&*()_+=-]{6,32}$/

const handleRegister = () => {
  error.value = ''
  success.value = false

  if (!email.value || !password.value || !repeat.value) {
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

  success.value = true

  setTimeout(() => {
    loginAs(email.value)
    router.push({ name: 'home' }).catch(() => {})
  }, 1200)
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
