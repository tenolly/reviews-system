<template>
  <div class="dashboard container">
    <header class="page-header">
      <h1>Панель администратора</h1>
      <p class="subtitle">Следите за динамикой отзывов, управляйте спорными материалами и статусами пользователей.</p>
    </header>

    <p v-if="actionLog" class="action-feedback">{{ actionLog }}</p>
    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
    <p v-else-if="loading" class="info-banner">Загружаем данные админки...</p>

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
            <h3>{{ item.teacher_name || `Преподаватель ${item.teacher}` }}</h3>
            <p>{{ item.comment || 'Комментарий отсутствует' }}</p>
            <div class="meta-row">
              <span class="meta-chip">Автор: {{ item.owner }}</span>
              <span class="meta-chip">Предмет: {{ item.subject_name || '—' }}</span>
              <span class="meta-chip">Создан: {{ formatDate(item.created_at) }}</span>
            </div>
          </div>
          <button type="button" class="btn danger small" :disabled="loading" @click="removeFlaggedReview(item.id)">
            Удалить отзыв
          </button>
        </li>
      </ul>
      <p v-if="!flaggedReviews.length && !loading" class="empty-state">Все спорные отзывы обработаны. Новых обращений нет.</p>
    </section>

    <section class="card admin-controls">
      <div class="admin-section-header">
        <h2>Управление пользователями</h2>
        <p>Быстро блокируйте или возвращайте доступ активным участникам дискуссий.</p>
      </div>
      <ul class="admin-list">
        <li v-for="user in managedUsers" :key="user.id" class="admin-item">
          <div class="admin-item-info">
            <h3>{{ user.username }}</h3>
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
            :disabled="loading"
            @click="toggleUserBan(user.id)"
          >
            {{ user.banned ? 'Снять бан' : 'Забанить' }}
          </button>
        </li>
      </ul>
      <p v-if="!managedUsers.length && !loading" class="empty-state">Пользователи системы в штатном режиме.</p>
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
import { onBeforeUnmount, onMounted, ref } from 'vue'
import api from '../services/api'

const loading = ref(true)
const errorMessage = ref('')
const metricCards = ref([])
const ratingBreakdown = ref([])
const discussed = ref([])
const flaggedReviews = ref([])
const managedUsers = ref([])
const actionLog = ref('')

let feedbackTimerId = null

const ratingLabels = {
  overall: 'Общее впечатление',
  difficulty: 'Сложность',
  interesting: 'Интерес',
  responsibility: 'Организация',
  fairness: 'Справедливость'
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

const buildMetrics = (reviews, users) => {
  const uniqueTeachers = new Set(reviews.map((r) => r.teacher)).size
  const bannedUsers = users.filter((u) => u.banned).length
  return [
    { title: 'Всего отзывов', value: String(reviews.length), icon: 'RV' },
    { title: 'Активных преподавателей', value: String(uniqueTeachers), icon: 'PR' },
    { title: 'Заблокированных', value: String(bannedUsers), icon: 'BL' }
  ]
}

const buildRatingBreakdown = (reviews) => {
  const fields = Object.keys(ratingLabels)
  if (!reviews.length) {
    return fields.map((field) => ({ label: ratingLabels[field], value: 0 }))
  }

  const totals = fields.reduce((acc, field) => ({ ...acc, [field]: 0 }), {})
  reviews.forEach((review) => {
    fields.forEach((field) => {
      totals[field] += Number(review[field] || 0)
    })
  })

  return fields.map((field) => ({
    label: ratingLabels[field],
    value: reviews.length ? totals[field] / reviews.length : 0
  }))
}

const buildDiscussed = (reviews) => {
  const byTeacher = new Map()
  reviews.forEach((review) => {
    const id = review.teacher
    const base = byTeacher.get(id) || {
      id,
      name: review.teacher_name || `Преподаватель ${id}`,
      reviews: 0,
      ratingSum: 0,
      tags: new Set()
    }

    base.reviews += 1
    base.ratingSum += Number(review.overall || 0)
    if (Array.isArray(review.tags)) {
      review.tags.forEach((tag) => base.tags.add(tag))
    }
    byTeacher.set(id, base)
  })

  return Array.from(byTeacher.values())
    .map((item) => ({
      id: item.id,
      name: item.name,
      reviews: item.reviews,
      rating: item.reviews ? item.ratingSum / item.reviews : 0,
      tags: Array.from(item.tags).slice(0, 4)
    }))
    .sort((a, b) => b.reviews - a.reviews)
    .slice(0, 5)
}

const formatDate = (value) => {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleDateString('ru-RU')
  } catch (error) {
    return String(value)
  }
}

const fetchDashboardData = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const [reviews, users] = await Promise.all([
      api.fetchAdminReviews(),
      api.fetchAdminUsers()
    ])

    flaggedReviews.value = reviews
    managedUsers.value = users
    metricCards.value = buildMetrics(reviews, users)
    ratingBreakdown.value = buildRatingBreakdown(reviews)
    discussed.value = buildDiscussed(reviews)
  } catch (error) {
    console.error('Не удалось загрузить данные админки', error)
    errorMessage.value = 'Не удалось загрузить данные админки. Попробуйте обновить страницу.'
  } finally {
    loading.value = false
  }
}

const removeFlaggedReview = async (id) => {
  try {
    await api.deleteAdminReview(id)
    flaggedReviews.value = flaggedReviews.value.filter((item) => item.id !== id)
    setActionFeedback(`Отзыв ${id} удалён из системы.`)
    metricCards.value = buildMetrics(flaggedReviews.value, managedUsers.value)
    ratingBreakdown.value = buildRatingBreakdown(flaggedReviews.value)
    discussed.value = buildDiscussed(flaggedReviews.value)
  } catch (error) {
    console.warn('Ошибка удаления отзыва', error)
    setActionFeedback('Не удалось удалить отзыв. Попробуйте позже.')
  }
}

const toggleUserBan = async (userId) => {
  try {
    const updated = await api.toggleAdminBan(userId)
    managedUsers.value = managedUsers.value.map((user) =>
      user.id === userId ? { ...user, banned: Boolean(updated.banned) } : user
    )
    setActionFeedback(updated.banned ? 'Пользователь заблокирован.' : 'Пользователь снова активен.')
    metricCards.value = buildMetrics(flaggedReviews.value, managedUsers.value)
  } catch (error) {
    console.warn('Ошибка смены статуса бана', error)
    setActionFeedback('Не удалось изменить статус пользователя.')
  }
}

onMounted(() => {
  void fetchDashboardData()
})

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

.info-banner,
.error-banner {
  margin: 12px 0 0;
  padding: 14px 18px;
  border-radius: 12px;
  font-weight: 600;
}

.info-banner {
  background: rgba(59, 130, 246, 0.14);
  color: var(--color-primary);
}

.error-banner {
  background: rgba(239, 68, 68, 0.14);
  color: var(--color-error);
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
