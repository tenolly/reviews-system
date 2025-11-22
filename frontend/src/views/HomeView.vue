<template>
  <div class="home container">
    <section class="hero card">
      <div class="hero-content">
        <h1>Центр отзывов о преподавателях</h1>
        <p>
          Изучайте честные отзывы студентов, находите сильных преподавателей и делитесь своим опытом, чтобы помочь другим сделать правильный выбор.
        </p>
        <div class="cta-row">
          <button type="button" class="btn primary" @click="goSearch">Найти преподавателя</button>
          <button
            v-if="isAuthenticated && !isBanned"
            type="button"
            class="btn outline"
            @click="goRate"
          >
            Оставить отзыв
          </button>
          <router-link v-if="!isAuthenticated && !isBanned" class="btn ghost" to="/login">
            Войти
          </router-link>
          <router-link v-if="!isAuthenticated && !isBanned" class="btn ghost" to="/register">
            Зарегистрироваться
          </router-link>
          <router-link v-if="isAdmin && !isBanned" class="btn minimal" to="/dashboard">
            Панель администратора
          </router-link>
        </div>
      </div>
      <div class="hero-illustration">
        <div class="chart"></div>
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
      </div>
    </section>

    <section class="features">
      <div class="card feature-card" v-for="feature in features" :key="feature.title">
        <div class="feature-icon">{{ feature.icon }}</div>
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.subtitle }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/mockAuth'

const router = useRouter()
const { user, isAuthenticated, isAdmin } = useAuthStore()

const isBanned = computed(() => user.value.banned)

const features = ref([])

const loadFeatures = () => {
  features.value = getFeaturesMock()
}

const getFeaturesMock = () => [
  {
    title: 'Умный поиск',
    subtitle: 'Фильтруйте преподавателей по имени, тегам и показателям, чтобы быстро найти подходящего человека.',
    icon: '1'
  },
  {
    title: 'Структурированная оценка',
    subtitle: 'Оценивайте разные аспекты работы: сложность, справедливость, вовлеченность и организованность.',
    icon: '2'
  },
  {
    title: 'Понятные дашборды',
    subtitle: 'Давайте администраторам прозрачную картину качества преподавания и удовлетворенности студентов.',
    icon: '3'
  }
]

loadFeatures()

const goSearch = () => {
  router.push('/search').catch(() => {})
}

const goRate = () => {
  router.push('/rate').catch(() => {})
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.hero {
  display: flex;
  gap: 40px;
  padding: 48px;
  align-items: center;
}

.hero-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-content h1 {
  font-size: 42px;
  margin: 0;
  color: var(--color-text);
}

.hero-content p {
  margin: 0;
  font-size: 18px;
  line-height: 1.6;
  color: var(--color-muted);
}

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-illustration {
  width: 280px;
  height: 240px;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.12), rgba(59, 130, 246, 0.02));
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
  padding: 24px;
}

.hero-illustration .chart {
  position: absolute;
  top: 28px;
  left: 50%;
  transform: translateX(-50%);
  width: 140px;
  height: 140px;
  border-radius: 24px;
  background: rgba(59, 130, 246, 0.18);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.hero-illustration .bar {
  width: 36px;
  height: 90px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
  border-radius: 18px 18px 6px 6px;
  opacity: 0.65;
}

.hero-illustration .bar:nth-child(3) {
  height: 120px;
  opacity: 0.85;
}

.hero-illustration .bar:nth-child(4) {
  height: 70px;
  opacity: 0.5;
}

.features {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.feature-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 24px;
  background: rgba(59, 130, 246, 0.12);
}

.feature-card h3 {
  margin: 0;
  font-size: 20px;
  color: var(--color-primary);
}

.feature-card p {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.5;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    padding: 28px;
    text-align: center;
  }

  .hero-content {
    align-items: center;
  }

  .hero-content h1 {
    font-size: 32px;
  }
}
</style>
