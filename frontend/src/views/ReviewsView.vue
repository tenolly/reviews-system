<template>
  <div class="reviews container" v-if="teacher">
    <div class="layout">
      <aside class="card teacher-panel">
        <div class="profile">
          <img :src="teacher.photo" :alt="teacher.fullName" />
          <div class="profile-info">
            <h1>{{ teacher.fullName }}</h1>
            <p class="subtitle">Табельный номер: {{ teacher.staffId }}</p>
            <div class="rating-block">
              <div class="rating-value">{{ teacher.average.toFixed(1) }}</div>
              <div class="rating-meta">
                <span>Средняя оценка</span>
                <span class="count">{{ teacher.reviewCount }} отзывов</span>
              </div>
            </div>
          </div>
        </div>
        <div class="metrics">
          <div v-for="metric in teacher.metrics" :key="metric.key" class="metric">
            <span class="metric-label">{{ metric.label }}</span>
            <div class="meter">
              <div class="meter-fill" :style="{ width: `${(metric.score / 5) * 100}%` }"></div>
            </div>
            <span class="metric-score">{{ metric.score.toFixed(1) }}</span>
          </div>
        </div>
        <div v-if="teacherContacts.length" class="contacts">
          <h2>Контакты</h2>
          <div v-for="contact in teacherContacts" :key="contact.key" class="contact-row">
            <span class="contact-label">{{ contact.label }}</span>
            <span class="contact-value">{{ contact.value }}</span>
          </div>
        </div>
        <div v-if="teacher.tags && teacher.tags.length" class="tag-list">
          <span v-for="tag in teacher.tags" :key="tag.id || tag.name" class="tag">
            #{{ tag.name }} ({{ tag.count }})
          </span>
        </div>
      </aside>

      <div class="reviews-column" ref="reviewsColumnRef">
        <section
          v-if="userReviewVisible"
          class="card user-review"
          :class="{ collapsed: userReview && userReviewCollapsed }"
        >
          <header class="user-review-header">
            <div>
              <h2>{{ userReview ? 'Ваш отзыв' : 'Оставьте отзыв' }}</h2>
              <p class="hint">
                {{ userReview ? 'Можно редактировать в любое время' : 'После публикации отзыв появится здесь' }}
              </p>
            </div>
            <div v-if="userReview" class="user-review-controls">
              <button type="button" class="toggle-btn" @click="toggleUserReviewCollapsed">
                {{ userReviewCollapsed ? 'Развернуть' : 'Свернуть' }}
              </button>
              <div class="actions" :class="{ hidden: userReviewCollapsed }">
                <button type="button" class="btn ghost" @click="goEdit">Изменить</button>
                <button type="button" class="btn danger" @click="showDeleteModal = true">Удалить</button>
              </div>
            </div>
          </header>

          <transition
            name="collapse-fade"
            @enter="handleCollapseEnter"
            @after-enter="handleCollapseAfterEnter"
            @leave="handleCollapseLeave"
            @after-leave="handleCollapseAfterLeave"
          >
            <div v-if="userReview && !userReviewCollapsed" class="user-review-body">
              <div class="user-review-top">
                <div class="score-anchor">
                  <button
                    type="button"
                    class="score-chip"
                    :class="toneClass(userReview.score)"
                    @click.stop="toggleBreakdown('user')"
                  >
                    {{ userReview.score.toFixed(1) }}
                  </button>
                  <div
                    v-if="isBreakdownVisible('user') && userReview.breakdown && userReview.breakdown.length"
                    class="score-popover"
                  >
                    <div class="popover-title">Расшифровка оценки</div>
                    <div v-for="metric in userReview.breakdown" :key="metric.key" class="popover-row">
                      <span>{{ metric.label }}</span>
                      <span>{{ metric.value.toFixed(1) }}</span>
                    </div>
                  </div>
                </div>
                <p class="meta">
                  Опубликован {{ formatDateTime(userReview.createdAt) }}
                  <span v-if="userReview.isEdited" class="edited" :title="formatDateTime(userReview.updatedAt)">
                    (изменен)
                  </span>
                </p>
              </div>
              <p v-if="userReview.subjectName" class="item-subject">Дисциплина: {{ userReview.subjectName }}</p>
              <div v-if="userReview.tags && userReview.tags.length" class="item-tags">
                <span v-for="tag in userReview.tags" :key="tag" class="tag muted">#{{ tag }}</span>
              </div>
              <p class="comment">{{ userReview.comment }}</p>
            </div>
          </transition>

          <div v-if="!userReview" class="empty-state">
            <h2>Вы ещё не оставили отзыв</h2>
            <p>Расскажите, как прошли занятия — ваша оценка поможет другим студентам.</p>
            <button type="button" class="btn primary" @click="goRate">Перейти к оцениванию</button>
          </div>
        </section>

        <section class="card review-list">
          <div class="list-header">
            <h2>Последние отзывы</h2>
            <p class="hint">Автосортировка: сначала новые</p>
            <p v-if="isAdmin" class="hint admin-hint">Администраторы могут удалить любой отзыв из списка.</p>
          </div>

          <div v-for="review in pagedReviews" :key="review.id" class="review-item">
            <div class="item-header">
              <div class="avatar">
                <img
                  v-if="review.photo"
                  :src="review.photo"
                  :alt="`Аватар пользователя ${review.author}`"
                  loading="lazy"
                />
                <span v-else class="avatar-fallback" aria-hidden="true">{{ review.initials }}</span>
              </div>
              <div class="item-body">
                <div class="item-top">
                  <div class="item-meta">
                    <div class="author">
                      {{ review.author }}
                      <span
                        v-if="review.isEdited"
                        class="edited"
                        :title="formatDateTime(review.updatedAt)"
                        aria-label="Отзыв был отредактирован"
                      >
                      (отзыв был изменен)
                      </span>
                    </div>
                    <time class="item-date" :datetime="review.createdAt">
                      {{ formatDateTime(review.createdAt) }}
                    </time>
                  </div>
                  <div class="score-wrapper">
                    <div class="score-anchor">
                      <button
                        type="button"
                        class="score-chip"
                        :class="toneClass(review.score)"
                        @click.stop="toggleBreakdown(review.id)"
                      >
                        {{ review.score.toFixed(1) }}
                      </button>
                      <div
                        v-if="isBreakdownVisible(review.id) && review.breakdown && review.breakdown.length"
                        class="score-popover"
                      >
                        <div class="popover-title">Расшифровка оценки</div>
                        <div v-for="metric in review.breakdown" :key="metric.key" class="popover-row">
                          <span>{{ metric.label }}</span>
                          <span>{{ metric.value.toFixed(1) }}</span>
                        </div>
                      </div>
                    </div>
                    <button v-if="isAdmin" type="button" class="btn ghost small">Удалить</button>
                  </div>
                </div>
              </div>
            </div>

            <p v-if="review.subjectName" class="item-subject">Дисциплина: {{ review.subjectName }}</p>
            <p class="item-comment">{{ review.comment }}</p>
            <div class="item-tags">
              <span v-for="tag in review.tags" :key="tag" class="tag muted">#{{ tag }}</span>
            </div>
          </div>

          <p v-if="!pagedReviews.length" class="empty">Пока нет отзывов. Станьте первым и поделитесь опытом.</p>

          <PaginationControls
            v-if="totalPages > 1"
            :current-page="currentPage"
            :total-pages="totalPages"
            @update:currentPage="handlePageChange"
          />
        </section>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-backdrop" role="dialog" aria-modal="true">
      <div class="modal card">
        <h3>Подтверждение удаления</h3>
        <p>Удаление отзыва нельзя отменить. Вы уверены, что хотите продолжить?</p>
        <div class="modal-actions">
          <button type="button" class="btn ghost" @click="showDeleteModal = false">Отмена</button>
          <button type="button" class="btn danger" @click="confirmDelete">Удалить</button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="container">
    <section class="card">
      <h1>Преподаватель не найден</h1>
      <p>Вернитесь на страницу поиска и выберите другую карточку.</p>
      <button type="button" class="btn primary" @click="goSearch">К списку преподавателей</button>
    </section>
  </div>
</template>

<script setup>
/* global defineProps */
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PaginationControls from '../components/common/PaginationControls.vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../services/api'

const props = defineProps({
  teacherId: {
    type: [String, Number],
    default: null
  }
})

const router = useRouter()
const { user, isAuthenticated, isAdmin } = useAuthStore()

const LAST_TEACHER_KEY = 'last_teacher_id'

const teacherBase = ref(null)
const teacherMetrics = ref({ rating: 0, metrics: [], reviewCount: 0 })
const reviewsSource = ref([])
const userReviewSource = ref(null)
const reviewsColumnRef = ref(null)
const activeBreakdown = ref({ id: null })
const userReviewCollapsed = ref(false)
const userReviewVisible = ref(true)
const showDeleteModal = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const saveLastTeacher = (id) => {
  if (typeof window === 'undefined') return
  try {
    if (id) {
      window.localStorage.setItem(LAST_TEACHER_KEY, String(id))
    }
  } catch (e) {
    console.warn('Не удалось сохранить последнего преподавателя', e)
  }
}

const getLastTeacher = () => {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage.getItem(LAST_TEACHER_KEY)
  } catch (e) {
    return null
  }
}

const reviewMetricDefinitions = [
  { key: 'overall', label: 'Общее впечатление' },
  { key: 'difficulty', label: 'Сложность' },
  { key: 'interesting', label: 'Интерес' },
  { key: 'responsibility', label: 'Организованность' },
  { key: 'fairness', label: 'Справедливость' }
]

const isBanned = computed(() => user.value.banned)

const teacher = computed(() => {
  if (!teacherBase.value) {
    return null
  }
  return {
    ...teacherBase.value,
    average: teacherMetrics.value.rating ?? 0,
    reviewCount: teacherMetrics.value.reviewCount ?? 0,
    metrics: teacherMetrics.value.metrics ?? []
  }
})

const teacherContacts = computed(() => {
  const contacts = teacherBase.value?.contacts ?? []
  if (Array.isArray(contacts)) {
    return contacts.map((item, index) => ({
      key: `contact-${index}`,
      label: 'Контакт',
      value: String(item)
    }))
  }

  const objectContacts = teacherBase.value?.contacts ?? {}
  const items = []
  if (objectContacts.phone) items.push({ key: 'phone', label: 'Телефон', value: objectContacts.phone })
  if (objectContacts.email) items.push({ key: 'email', label: 'Почта', value: objectContacts.email })
  if (objectContacts.telegram) items.push({ key: 'telegram', label: 'Telegram', value: objectContacts.telegram })
  if (objectContacts.office) items.push({ key: 'office', label: 'Аудитория', value: objectContacts.office })
  if (objectContacts.site) items.push({ key: 'site', label: 'Сайт', value: objectContacts.site })
  return items
})

const userReview = computed(() => {
  if (!isAuthenticated.value || isBanned.value || user.value.role === 'admin') {
    return null
  }
  return userReviewSource.value
})

const toneClass = (score) => {
  const normalized = Math.max(1, Math.min(5, score || 0))
  if (normalized >= 4.5) return 'tone-5'
  if (normalized >= 3.75) return 'tone-4'
  if (normalized >= 3) return 'tone-3'
  if (normalized >= 2.25) return 'tone-2'
  return 'tone-1'
}

const computeScore = (review) => {
  const fields = ['overall', 'difficulty', 'interesting', 'responsibility', 'fairness']
  const values = fields.map((field) => Number(review[field]) || 0)
  const sum = values.reduce((acc, value) => acc + value, 0)
  return Number((sum / fields.length).toFixed(2))
}

const buildBreakdown = (review) =>
  reviewMetricDefinitions.map((metric) => ({
    key: metric.key,
    label: metric.label,
    value: Number(review[metric.key] ?? 0)
  }))

const aggregateMetrics = (reviews = []) => {
  if (!reviews.length) {
    return {
      rating: 0,
      metrics: reviewMetricDefinitions.map((metric) => ({ key: metric.key, label: metric.label, score: 0 })),
      reviewCount: 0
    }
  }

  const totals = {
    overall: 0,
    difficulty: 0,
    interesting: 0,
    responsibility: 0,
    fairness: 0
  }

  reviews.forEach((review) => {
    Object.keys(totals).forEach((key) => {
      const value = Number(review[key]) || 0
      totals[key] += value
    })
  })

  const metrics = reviewMetricDefinitions.map((metric) => ({
    key: metric.key,
    label: metric.label,
    score: Number((totals[metric.key] / reviews.length).toFixed(2))
  }))

  const rating = metrics.reduce((acc, metric) => acc + metric.score, 0) / metrics.length

  return {
    rating: Number(rating.toFixed(2)),
    metrics,
    reviewCount: reviews.length
  }
}

const mapReview = (review) => {
  const score = computeScore(review)
  return {
    id: review.id,
    author: review.owner || 'Неизвестно',
    owner: review.owner,
    initials: (review.owner || 'NA').slice(0, 2).toUpperCase(),
    score,
    createdAt: review.created_at || new Date().toISOString(),
    updatedAt: review.updated_at || review.created_at || new Date().toISOString(),
    isEdited: Boolean(review.is_edited),
    comment: review.comment || '',
    tags: review.tags || [],
    subjectId: review.subject,
    subjectName: review.subject_name || review.subject,
    breakdown: buildBreakdown(review),
    photo: review.photo_url || ''
  }
}

const loadTeacher = async () => {
  const fallback = 'Не удалось загрузить данные преподавателя.'
  try {
    const lastTeacherId = props.teacherId || getLastTeacher()

    if (lastTeacherId) {
      try {
        const data = await api.fetchTeacher(lastTeacherId)
        teacherBase.value = {
          id: data.id,
          isu: data.isu,
          fullName: data.name,
          staffId: data.isu,
          photo: data.photo_url || 'https://via.placeholder.com/160x160.png?text=RS',
          tags: (data.tags || []).map((tag) => ({
            id: String(tag.id ?? tag.name),
            name: tag.name || String(tag.id),
            count: tag.count ?? 0
          })),
          contacts: data.contacts || []
        }
        saveLastTeacher(data.id)
        return
      } catch (error) {
        console.warn('Не удалось загрузить преподавателя по сохраненному id', error)
      }
    }

    const list = await api.fetchTeachers()
    if (list && list.length) {
      const entry = list[0]
      teacherBase.value = {
        id: entry.id,
        isu: entry.isu,
        fullName: entry.name,
        staffId: entry.isu,
        photo: entry.photo_url || 'https://via.placeholder.com/160x160.png?text=RS',
        tags: (entry.tags || []).map((tag) => ({
          id: String(tag.id ?? tag.name),
          name: tag.name || String(tag.id),
          count: tag.count ?? 0
        })),
        contacts: entry.contacts || []
      }
      saveLastTeacher(entry.id)
      return
    }

    errorMessage.value = fallback
  } catch (error) {
    console.error(fallback, error)
    errorMessage.value = fallback
  }
}

const loadReviews = async () => {
  if (!teacherBase.value?.isu) {
    reviewsSource.value = []
    teacherMetrics.value = { rating: 0, metrics: [], reviewCount: 0 }
    return
  }
  try {
    const page = await api.fetchReviews({ teacherIsu: teacherBase.value.isu })
    const rawReviews = page?.results || []
    reviewsSource.value = rawReviews.map(mapReview)
    teacherMetrics.value = aggregateMetrics(rawReviews)

    saveLastTeacher(teacherBase.value.id)

    if (isAuthenticated.value) {
      userReviewSource.value = reviewsSource.value.find((review) => review.owner === user.value.username) || null
    } else {
      userReviewSource.value = null
    }
  } catch (error) {
    console.warn('Не удалось загрузить отзывы', error)
    reviewsSource.value = []
    teacherMetrics.value = { rating: 0, metrics: [], reviewCount: 0 }
  }
}

const refresh = async () => {
  loading.value = true
  errorMessage.value = ''
  await loadTeacher()
  await loadReviews()
  loading.value = false
}

onMounted(() => {
  void refresh()
})

watch(
  () => props.teacherId,
  () => {
    void refresh()
  }
)

const confirmDelete = async () => {
  if (!userReviewSource.value) {
    showDeleteModal.value = false
    return
  }
  try {
    await api.deleteReview(userReviewSource.value.id)
    await loadReviews()
  } catch (error) {
    console.error('Не удалось удалить отзыв', error)
  } finally {
    showDeleteModal.value = false
    activeBreakdown.value = { id: null }
    userReviewCollapsed.value = false
  }
}

const formatDateTime = (value) => {
  const dt = new Date(value)
  return dt.toLocaleString(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const toggleUserReviewCollapsed = () => {
  userReviewCollapsed.value = !userReviewCollapsed.value
  if (userReviewCollapsed.value) {
    activeBreakdown.value = { id: null }
  }
}

const goRate = () => {
  router.push({ name: 'rate', query: { teacherId: teacher.value?.id ?? '' } }).catch(() => {})
}

const goEdit = () => {
  router.push({ name: 'rate', query: { teacherId: teacher.value?.id ?? '', edit: 'true' } }).catch(() => {})
}

const goSearch = () => {
  router.push({ name: 'search' }).catch(() => {})
}

const sortedReviews = computed(() =>
  [...reviewsSource.value].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
)

const currentPage = ref(1)
const pageSize = 10

const totalPages = computed(() => Math.max(1, Math.ceil(sortedReviews.value.length / pageSize)))

const pagedReviews = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedReviews.value.slice(start, start + pageSize)
})

const hasBreakdown = (targetId) => {
  if (targetId === 'user') {
    return Boolean(userReview.value && userReview.value.breakdown && userReview.value.breakdown.length)
  }
  const review = reviewsSource.value.find((item) => item.id === targetId)
  return Boolean(review && review.breakdown && review.breakdown.length)
}

const scrollReviewsToTop = () => {
  const el = reviewsColumnRef.value
  if (!el) {
    return
  }

  const scrollContainer = () => {
    if (typeof el.scrollTo === 'function') {
      el.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      el.scrollTop = 0
    }
  }

  if (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function') {
    window.requestAnimationFrame(scrollContainer)
  } else {
    scrollContainer()
  }

  if (typeof window !== 'undefined') {
    const rect = el.getBoundingClientRect()
    const offset = Math.max(0, rect.top + window.scrollY - 120)
    window.scrollTo({ top: offset, behavior: 'smooth' })
  }
}

const collapseTransition = 'height 0.3s ease, opacity 0.22s ease'

const runOnNextFrame = (callback) => {
  if (typeof window === 'undefined' || typeof window.requestAnimationFrame !== 'function') {
    callback()
    return
  }
  window.requestAnimationFrame(callback)
}

const resetCollapseStyles = (el) => {
  el.style.height = ''
  el.style.opacity = ''
  el.style.overflow = ''
  el.style.transition = ''
}

const handleCollapseEnter = (el) => {
  if (!el) {
    return
  }
  el.style.height = '0px'
  el.style.opacity = '0'
  el.style.overflow = 'hidden'
  el.style.transition = collapseTransition
  runOnNextFrame(() => {
    el.style.height = `${el.scrollHeight}px`
    el.style.opacity = '1'
  })
}

const handleCollapseAfterEnter = (el) => {
  if (!el) {
    return
  }
  resetCollapseStyles(el)
}

const handleCollapseLeave = (el) => {
  if (!el) {
    return
  }
  el.style.height = `${el.scrollHeight}px`
  el.style.opacity = '1'
  el.style.overflow = 'hidden'
  el.style.transition = collapseTransition
  runOnNextFrame(() => {
    el.style.height = '0px'
    el.style.opacity = '0'
  })
}

const handleCollapseAfterLeave = (el) => {
  if (!el) {
    return
  }
  resetCollapseStyles(el)
}

const toggleBreakdown = (targetId) => {
  if (!hasBreakdown(targetId)) {
    return
  }
  activeBreakdown.value = activeBreakdown.value.id === targetId ? { id: null } : { id: targetId }
}

const isBreakdownVisible = (targetId) => activeBreakdown.value.id === targetId

const handlePageChange = async (page) => {
  currentPage.value = page
  activeBreakdown.value = { id: null }
  await nextTick()
  scrollReviewsToTop()
}
</script>

<style scoped>
.reviews {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.layout {
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(320px, 1fr) minmax(0, 2fr);
  align-items: flex-start;
}

.teacher-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 120px;
  min-height: 50vh;
  font-size: 14px;
}

.reviews-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
  padding-right: 12px;
  scroll-behavior: smooth;
}

.profile {
  display: flex;
  gap: 24px;
  align-items: center;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(59, 130, 246, 0.3);
}

.profile h1 {
  margin: 0;
  color: var(--color-text);
  font-size: 28px;
  line-height: 1.2;
}

.subtitle {
  margin: 4px 0 12px;
  color: var(--color-muted);
  font-size: 14px;
}

.rating-block {
  display: flex;
  align-items: center;
  gap: 16px;
}

.rating-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-primary);
}

.rating-meta {
  display: flex;
  flex-direction: column;
  color: var(--color-muted);
  font-weight: 600;
  font-size: 12px;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-label {
  flex: 1;
  font-weight: 600;
  color: var(--color-muted);
}

.meter {
  flex: 1.6;
  height: 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.16);
  position: relative;
  overflow: hidden;
}

.meter-fill {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.metric-score {
  font-weight: 600;
  color: var(--color-primary);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 12px;
}

.tag {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid var(--color-border);
  color: var(--color-primary);
  font-weight: 600;
  font-size: 12px;
}

.contacts {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contacts h2 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}

.contact-row {
  display: flex;
  gap: 8px;
  justify-content: space-between;
  color: var(--color-muted);
  font-size: 14px;
  flex-wrap: wrap;
}

.contact-label {
  font-weight: 600;
  color: var(--color-text);
}

.contact-value {
  word-break: break-word;
}

.user-review {
  position: relative;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-review.collapsed {
  padding-bottom: 20px;
}

.user-review header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.user-review-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  border: none;
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.16);
  color: var(--color-muted);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.toggle-btn:hover {
  background: rgba(148, 163, 184, 0.26);
}

.toggle-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.actions {
  display: flex;
  gap: 12px;
}

.actions.hidden {
  display: none;
}

.collapse-fade-enter-active,
.collapse-fade-leave-active {
  transition: opacity 0.22s ease;
}

.collapse-fade-enter-from,
.collapse-fade-leave-to {
  opacity: 0;
}

.user-review-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-review-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.score-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.comment {
  margin: 0 0 8px;
  line-height: 1.6;
  color: var(--color-text);
}

.meta {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.edited {
  color: var(--color-muted);
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: help;
}

.item-subject {
  margin: 0;
  color: var(--color-muted);
  font-weight: 600;
  font-size: 13px;
}

.empty-state {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.list-header h2 {
  margin: 0;
}

.hint {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.admin-hint {
  color: var(--color-primary);
}

.review-item {
  position: relative;
  padding: 18px 0 18px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 14px;
}


.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(59, 130, 246, 0.16);
  display: grid;
  place-items: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-fallback {
  font-weight: 700;
  color: var(--color-primary);
}

.author {
  font-weight: 600;
  color: var(--color-text);
}

.item-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  position: relative;
}

.item-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-date {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-muted);
}

.score-chip {
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 6px 12px;
  font-weight: 600;
  background: var(--score-chip-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.score-chip:hover {
  box-shadow: 0 6px 14px var(--score-chip-hover-shadow);
}

.score-chip:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.tone-1 {
  background: var(--tone-1-bg);
  color: var(--tone-1-text);
  border-color: rgba(220, 38, 38, 0.4);
}

.tone-2 {
  background: var(--tone-2-bg);
  color: var(--tone-2-text);
  border-color: rgba(217, 119, 6, 0.45);
}

.tone-3 {
  background: var(--tone-3-bg);
  color: var(--tone-3-text);
  border-color: rgba(202, 138, 4, 0.4);
}

.tone-4 {
  background: var(--tone-4-bg);
  color: var(--tone-4-text);
  border-color: rgba(34, 197, 94, 0.4);
}

.tone-5 {
  background: var(--tone-5-bg);
  color: var(--tone-5-text);
  border-color: rgba(22, 163, 74, 0.45);
}

.score-anchor {
  position: relative;
  display: inline-flex;
}

.score-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 210px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-popover);
  padding: 14px 16px;
  z-index: 20;
}

.user-review .score-popover {
  right: auto;
  left: 0;
}

.popover-title {
  font-weight: 700;
  font-size: 13px;
  color: var(--color-text);
  margin-bottom: 8px;
}

.popover-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--color-muted);
}

.popover-row span:last-child {
  font-weight: 600;
  color: var(--color-primary);
}

.btn.danger {
  background: rgba(220, 38, 38, 0.15);
  color: var(--color-error);
  transition: background-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}

.btn.danger:hover {
  background: rgba(220, 38, 38, 0.24);
  box-shadow: 0 6px 18px rgba(220, 38, 38, 0.2);
}
.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.item-comment {
  margin: 0;
  color: var(--color-text);
  line-height: 1.6;
}

.item-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag.muted {
  background: var(--chip-bg);
  border-color: var(--chip-border);
  color: var(--color-muted);
}

:global([data-theme='dark']) .tag {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
  color: #e0eaff;
}

:global([data-theme='dark']) .tag.muted {
  background: rgba(15, 23, 42, 0.45);
  border-color: rgba(148, 163, 184, 0.4);
}

.empty {
  text-align: center;
  color: var(--color-muted);
  margin: 24px 0;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: grid;
  place-items: center;
  z-index: 30;
}

.modal {
  max-width: 360px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .teacher-panel {
    position: static;
    min-height: auto;
  }

  .reviews-column {
    max-height: none;
    overflow: visible;
    padding-right: 0;
  }

  .profile {
    flex-direction: column;
    text-align: center;
  }

  .metrics {
    grid-template-columns: 1fr;
  }

  .score-wrapper {
    align-items: flex-start;
  }

  .score-popover {
    position: static;
    width: 100%;
    margin-top: 12px;
  }

  .item-header {
    align-items: flex-start;
  }

  .item-top {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 1024px) {
  .layout {
    grid-template-columns: minmax(280px, 1fr) minmax(0, 1.6fr);
  }

  .reviews-column {
    max-height: calc(100vh - 240px);
  }
}
</style>
