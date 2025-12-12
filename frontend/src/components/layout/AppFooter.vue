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
  background: var(--color-surface);
  color: var(--color-text);
  border-top: 1px solid var(--color-border);
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
  color: #ffffff;
  font-weight: 700;
}

.title {
  font-weight: 600;
  font-size: 16px;
}

.subtitle {
  font-size: 13px;
  color: var(--color-muted);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 18px;
}

.footer-links a {
  color: var(--color-primary);
  font-size: 14px;
}

.footer-links a:hover {
  color: var(--color-primary-dark);
}

.footer-meta {
  font-size: 13px;
  color: var(--color-muted);
}

:global([data-theme='dark']) .app-footer {
  background: #0f172a;
  color: rgba(255, 255, 255, 0.88);
}

:global([data-theme='dark']) .footer-links a {
  color: rgba(255, 255, 255, 0.7);
}

:global([data-theme='dark']) .footer-links a:hover {
  color: #ffffff;
}

:global([data-theme='dark']) .footer-meta {
  color: rgba(255, 255, 255, 0.7);
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
