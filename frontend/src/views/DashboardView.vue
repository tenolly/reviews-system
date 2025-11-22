<template>
  <div class="dashboard container">
    <header class="page-header">
      <h1>Панель администратора</h1>
      <p class="subtitle">Следите за динамикой отзывов, управляйте спорными материалами и статусами пользователей.</p>
    </header>

    <p v-if="actionLog" class="action-feedback">{{ actionLog }}</p>

    <section class="metrics">
      <div v-for="card in metricCards" :key="card.title" class="card metric-card">
        <div class="icon">{{ card.icon }}</div>
        <div>
          <div class="value">{{ card.value }}</div>
          <div class="label">{{ card.title }}</div>
        </div>
      </div>
    </section>

    <section class="card admin-controls">
      <div class="admin-section-header">
        <h2>Управление отзывами</h2>
        <p>Работайте со спорными комментариями, поступившими на ручную проверку.</p>
      </div>
      <ul class="admin-list">
        <li v-for="item in flaggedReviews" :key="item.id" class="admin-item">
          <div class="admin-item-info">
            <h3>{{ item.teacher }}</h3>
            <p>{{ item.reason }}</p>
            <div class="meta-row">
              <span class="meta-chip">Автор: {{ item.author }}</span>
              <span class="meta-chip">Поступил: {{ item.reportedAt }}</span>
            </div>
          </div>
          <button type="button" class="btn danger small" @click="removeFlaggedReview(item.id)">
            Удалить отзыв
          </button>
        </li>
      </ul>
      <p v-if="!flaggedReviews.length" class="empty-state">Все спорные отзывы обработаны. Новых обращений нет.</p>
    </section>

    <section class="card admin-controls">
      <div class="admin-section-header">
        <h2>Управление пользователями</h2>
        <p>Быстро блокируйте или возвращайте доступ активным участникам дискуссий.</p>
      </div>
      <ul class="admin-list">
        <li v-for="user in managedUsers" :key="user.id" class="admin-item">
          <div class="admin-item-info">
            <h3>{{ user.name }}</h3>
            <p>{{ user.email }}</p>
            <div class="meta-row">
              <span class="meta-chip">Отзывов: {{ user.reviews }}</span>
              <span class="status-pill" :class="{ banned: user.banned }">
                {{ user.banned ? 'Заблокирован' : 'Активен' }}
              </span>
            </div>
          </div>
          <button
            type="button"
            class="btn small"
            :class="user.banned ? 'outline' : 'danger'"
            @click="toggleUserBan(user.id)"
          >
            {{ user.banned ? 'Снять бан' : 'Забанить' }}
          </button>
        </li>
      </ul>
      <p v-if="!managedUsers.length" class="empty-state">Пользователи системы в штатном режиме.</p>
    </section>

    <section class="card charts">
      <h2>Средние оценки по параметрам</h2>
      <div class="bars">
        <div v-for="item in ratingBreakdown" :key="item.label" class="bar-row">
          <span class="label">{{ item.label }}</span>
          <div class="bar-shell">
            <div class="bar-fill" :style="{ width: item.value * 20 + '%' }"></div>
          </div>
          <span class="score">{{ item.value.toFixed(1) }}</span>
        </div>
      </div>
    </section>

    <section class="card table">
      <h2>Самые обсуждаемые преподаватели</h2>
      <table>
        <thead>
          <tr>
            <th>ФИО</th>
            <th>Отзывов (30 дн)</th>
            <th>Средний балл</th>
            <th>Популярные теги</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in discussed" :key="row.id">
            <td>{{ row.name }}</td>
            <td>{{ row.reviews }}</td>
            <td>{{ row.rating.toFixed(1) }}</td>
            <td>
              <span v-for="tag in row.tags" :key="tag" class="tag">#{{ tag }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref } from 'vue'

const metricCards = ref([])
const ratingBreakdown = ref([])
const discussed = ref([])
const flaggedReviews = ref([])
const managedUsers = ref([])
const actionLog = ref('')

let feedbackTimerId = null

const loadMetricCards = () => {
  metricCards.value = getMetricCardsMock()
}

const loadRatingBreakdown = () => {
  ratingBreakdown.value = getRatingBreakdownMock()
}

const loadDiscussed = () => {
  discussed.value = getDiscussedMock()
}

const loadFlaggedReviews = () => {
  flaggedReviews.value = getFlaggedReviewsMock()
}

const loadManagedUsers = () => {
  managedUsers.value = getManagedUsersMock()
}

const setActionFeedback = (message) => {
  actionLog.value = message
  if (feedbackTimerId) {
    clearTimeout(feedbackTimerId)
  }
  feedbackTimerId = setTimeout(() => {
    actionLog.value = ''
    feedbackTimerId = null
  }, 4000)
}

const removeFlaggedReview = (id) => {
  const record = flaggedReviews.value.find((item) => item.id === id)
  flaggedReviews.value = flaggedReviews.value.filter((item) => item.id !== id)
  if (record) {
    setActionFeedback(`Отзыв ${record.id.toUpperCase()} удалён из системы.`)
  }
}

const toggleUserBan = (userId) => {
  managedUsers.value = managedUsers.value.map((user) => {
    if (user.id !== userId) {
      return user
    }
    const nextState = { ...user, banned: !user.banned }
    setActionFeedback(
      nextState.banned
        ? `Пользователь ${nextState.name} временно заблокирован.`
        : `Пользователь ${nextState.name} снова активен.`
    )
    return nextState
  })
}

const getMetricCardsMock = () => [
  { title: 'Всего отзывов', value: '1 284', icon: 'RV' },
  { title: 'Активных преподавателей', value: '56', icon: 'IN' },
  { title: 'Помечено к проверке', value: '3', icon: 'FL' }
]

const getRatingBreakdownMock = () => [
  { label: 'Общее впечатление', value: 4.4 },
  { label: 'Сложность', value: 3.3 },
  { label: 'Интерес', value: 4.2 },
  { label: 'Организация', value: 4.5 },
  { label: 'Справедливость', value: 4.3 }
]

const getDiscussedMock = () => [
  { id: 't-1', name: 'Преподаватель 1', reviews: 32, rating: 4.6, tags: ['инновации', 'наставничество'] },
  { id: 't-2', name: 'Преподаватель 2', reviews: 27, rating: 4.1, tags: ['исследования', 'структура'] },
  { id: 't-3', name: 'Преподаватель 3', reviews: 21, rating: 3.8, tags: ['требовательность', 'точность'] }
]

const getFlaggedReviewsMock = () => [
  {
    id: 'rev-340',
    teacher: 'Преподаватель 5',
    author: 'Студент 24',
    reason: 'Жалоба модератора: оскорбительная лексика',
    reportedAt: '10 ноя 2025'
  },
  {
    id: 'rev-317',
    teacher: 'Преподаватель 3',
    author: 'Студент 4',
    reason: 'Автофильтр: подозрение на спам',
    reportedAt: '08 ноя 2025'
  }
]

const getManagedUsersMock = () => [
  {
    id: 'user-102',
    name: 'Студент 24',
    email: 'student24@example.com',
    reviews: 6,
    banned: false
  },
  {
    id: 'user-204',
    name: 'Студент 43',
    email: 'student43@example.com',
    reviews: 2,
    banned: true
  },
  {
    id: 'user-312',
    name: 'Студент 8',
    email: 'student8@example.com',
    reviews: 11,
    banned: false
  }
]

loadMetricCards()
loadRatingBreakdown()
loadDiscussed()
loadFlaggedReviews()
loadManagedUsers()

onBeforeUnmount(() => {
  if (feedbackTimerId) {
    clearTimeout(feedbackTimerId)
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.page-header h1 {
  margin: 0;
  color: var(--color-text);
}

.page-header .subtitle {
  margin: 8px 0 0;
  color: var(--color-muted);
}

.action-feedback {
  margin: 0;
  padding: 16px 20px;
  border-radius: 16px;
  background: rgba(34, 197, 94, 0.18);
  color: var(--color-success);
  font-weight: 600;
}

:global([data-theme='dark']) .action-feedback {
  background: rgba(34, 197, 94, 0.28);
  color: #34d399;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

.admin-controls {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.admin-section-header h2 {
  margin: 0;
  color: var(--color-text);
}

.admin-section-header p {
  margin: 6px 0 0;
  color: var(--color-muted);
}

.admin-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.admin-item-info {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.admin-item-info h3 {
  margin: 0;
  color: var(--color-text);
}

.admin-item-info p {
  margin: 0;
  color: var(--color-muted);
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.16);
  color: var(--color-primary);
  font-weight: 700;
  font-size: 12px;
}

.status-pill.banned {
  background: rgba(239, 68, 68, 0.18);
  color: var(--tone-1-text);
}

.empty-state {
  margin: 0;
  color: var(--color-muted);
  font-style: italic;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-card .icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(59, 130, 246, 0.12);
  font-size: 24px;
}

.metric-card .value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
}

.metric-card .label {
  color: var(--color-muted);
}

.charts {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.bars {
  display: grid;
  gap: 14px;
}

.bar-row {
  display: grid;
  grid-template-columns: 200px 1fr 60px;
  align-items: center;
  gap: 18px;
}

.bar-shell {
  height: 12px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.score {
  font-weight: 700;
  color: var(--color-primary);
}

.table {
  overflow-x: auto;
}

.table table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 14px;
  text-align: left;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}

.table th {
  color: var(--color-muted);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
}

.tag {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.16);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
}

@media (max-width: 900px) {
  .bar-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .admin-item {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-item button {
    width: 100%;
  }
}
</style>
