<template>
  <footer class="app-footer">
    <div class="container footer-inner">
      <div class="footer-brand">
        <span class="brand-icon">RS</span>
        <div>
          <div class="title">Система отзывов</div>
          <div class="subtitle">Прозрачная обратная связь для лучших занятий</div>
        </div>
      </div>
      <div class="footer-links">
        <router-link to="/">Главная</router-link>
        <router-link to="/search">Поиск</router-link>
        <router-link to="/reviews">Отзывы</router-link>
        <router-link to="/rate">Оценивание</router-link>
      </div>
      <div class="footer-meta">
        <span>&copy; {{ currentYear }} Система отзывов</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  padding: 32px 0;
  background: #0f172a;
  color: rgba(255, 255, 255, 0.88);
  margin-top: auto;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  font-weight: 700;
}

.title {
  font-weight: 600;
  font-size: 16px;
}

.subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 18px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.footer-links a:hover {
  color: #ffffff;
}

.footer-meta {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 768px) {
  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
  }

  .footer-links {
    flex-wrap: wrap;
  }
}
</style>
