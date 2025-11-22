<template>
  <div class="auth container">
    <section class="card form-card">
      <h1>С возвращением</h1>
      <p class="subtitle">Войдите с помощью корпоративной почты и пароля.</p>

      <form class="form" @submit.prevent="handleLogin">
        <label class="field">
          <span class="label">Электронная почта</span>
          <input v-model="email" type="email" required placeholder="user@example.com" />
        </label>

        <label class="field">
          <span class="label">Пароль</span>
          <input v-model="password" type="password" required placeholder="••••••" />
        </label>

        <button type="submit" class="btn primary">Войти</button>
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
import { loginAs } from '../stores/mockAuth'

const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')

const handleLogin = () => {
  if (!email.value || !password.value) {
    error.value = 'Заполните оба поля, чтобы продолжить.'
    return
  }

  loginAs(email.value)
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
  router.push(redirect).catch(() => {})
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
