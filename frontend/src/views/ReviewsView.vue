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
            <div class="tag-list">
              <span v-for="tag in teacher.tags" :key="tag" class="tag">#{{ tag }}</span>
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
                <p class="meta">Опубликован {{ formatDate(userReview.date) }}</p>
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
                    <div class="author">{{ review.author }}</div>
                    <time class="item-date" :datetime="review.date">{{ formatDate(review.date) }}</time>
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
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import PaginationControls from '../components/common/PaginationControls.vue'
import { useAuthStore } from '../stores/mockAuth'
import { getUserReviewMock } from '../mocks/userReview'

const props = defineProps({
  teacherId: {
    type: String,
    default: null
  }
})

const router = useRouter()
const { user, isAuthenticated, isAdmin } = useAuthStore()

const isBanned = computed(() => user.value.banned)

const teacherDirectory = ref([])
const reviewsSource = ref([])
const userReviewSource = ref(null)
const reviewsColumnRef = ref(null)
const activeBreakdown = ref({ id: null })
const userReviewCollapsed = ref(false)

const reviewMetricDefinitions = [
  { key: 'overall', label: 'Общее впечатление' },
  { key: 'difficulty', label: 'Сложность' },
  { key: 'interest', label: 'Интерес' },
  { key: 'organization', label: 'Организованность' },
  { key: 'fairness', label: 'Справедливость' }
]

const toneClass = (score) => {
  const normalized = Math.max(1, Math.min(5, score || 0))
  if (normalized >= 4.5) return 'tone-5'
  if (normalized >= 3.75) return 'tone-4'
  if (normalized >= 3) return 'tone-3'
  if (normalized >= 2.25) return 'tone-2'
  return 'tone-1'
}

const loadTeacherDirectory = () => {
  teacherDirectory.value = getTeacherDirectoryMock()
}

const loadReviews = () => {
  reviewsSource.value = getReviewsMock()
}

const loadUserReview = () => {
  userReviewSource.value = getUserReviewMock()
}

const getTeacherDirectoryMock = () => [
  {
    id: 't-1',
    fullName: 'Преподаватель 1',
    staffId: 'ID1000',
    photo: 'https://i.pravatar.cc/160?img=12',
    average: 4.6,
    reviewCount: 128,
    tags: ['инновации', 'поддержка', 'наставничество'],
    metrics: [
      { key: 'overall', label: 'Общее впечатление', score: 4.7 },
      { key: 'difficulty', label: 'Сложность', score: 3.2 },
      { key: 'interest', label: 'Интерес', score: 4.4 },
      { key: 'organization', label: 'Организованность', score: 4.8 },
      { key: 'fairness', label: 'Справедливость', score: 4.6 }
    ],
    contacts: {
      email: 'lecturer.quality@university.ru',
      phone: '+7 (900) 555-10-10',
      telegram: '@quality_teacher'
    }
  },
  {
    id: 't-2',
    fullName: 'Преподаватель 2',
    staffId: 'ID1001',
    photo: 'https://i.pravatar.cc/160?img=33',
    average: 4.1,
    reviewCount: 92,
    tags: ['исследования', 'структура', 'практика'],
    metrics: [
      { key: 'overall', label: 'Общее впечатление', score: 4.2 },
      { key: 'difficulty', label: 'Сложность', score: 3.6 },
      { key: 'interest', label: 'Интерес', score: 4.1 },
      { key: 'organization', label: 'Организованность', score: 4.0 },
      { key: 'fairness', label: 'Справедливость', score: 4.3 }
    ],
    contacts: {
      email: 'research.course@university.ru',
      office: 'Корпус Б, ауд. 312'
    }
  }
]

const buildTeacherMock = (teacherId) => {
  const index = Number(teacherId?.split('-')[1]) || 1
  const seed = index + 3
  const contacts = {}
  if (seed % 2 === 0) {
    contacts.email = `teacher${index}@university.ru`
  }
  if (seed % 3 === 0) {
    contacts.phone = `+7 (901) ${String(4000 + index * 7).padStart(4, '0')}-${String(20 + (index % 80)).padStart(2, '0')}`
  }
  if (seed % 5 === 0) {
    contacts.telegram = `@teacher_${index}`
  }
  if (seed % 7 === 0) {
    contacts.office = `Корпус ${String.fromCharCode(65 + (index % 4))}, ауд. ${210 + (index % 30)}`
  }

  const result = {
    id: teacherId,
    fullName: `Преподаватель ${index}`,
    staffId: `ID${1000 + index}`,
    photo: `https://i.pravatar.cc/160?img=${(index % 70) + 1}`,
    average: 3.6 + ((index * 9) % 15) / 10,
    reviewCount: 40 + (index % 30),
    tags: ['инновации', 'поддержка', index % 2 === 0 ? 'наставничество' : 'структура'],
    metrics: [
      { key: 'overall', label: 'Общее впечатление', score: 3.8 + ((index * 3) % 7) / 10 },
      { key: 'difficulty', label: 'Сложность', score: 3 + ((index * 5) % 6) / 10 },
      { key: 'interest', label: 'Интерес', score: 3.6 + ((index * 4) % 6) / 10 },
      { key: 'organization', label: 'Организованность', score: 3.9 + ((index * 2) % 6) / 10 },
      { key: 'fairness', label: 'Справедливость', score: 3.7 + ((index * 6) % 6) / 10 }
    ]
  }

  if (Object.keys(contacts).length) {
    result.contacts = contacts
  }

  return result
}

const buildBreakdownMock = (seedBase) =>
  reviewMetricDefinitions.map((metric, index) => {
    const seed = 3.2 + ((seedBase * 5 + index * 3) % 13) / 10
    const value = Math.min(4.9, Math.max(2.4, seed))
    return {
      key: metric.key,
      label: metric.label,
      value
    }
  })

const buildNegativeBreakdown = (seedBase) =>
  reviewMetricDefinitions.map((metric, index) => {
    const offset = ((seedBase + index * 2) % 4) * 0.18
    const value = Math.max(1.2, 2 - offset)
    return {
      key: metric.key,
      label: metric.label,
      value
    }
  })

const getReviewsMock = () => {
  return Array.from({ length: 18 }, (_, index) => {
    const author = `Студент ${index + 1}`
    const isNegative = (index + 1) % 5 === 0 || (index + 2) % 7 === 0
    const breakdown = isNegative ? buildNegativeBreakdown(index + 1) : buildBreakdownMock(index + 1)
    const score = breakdown.reduce((acc, metric) => acc + metric.value, 0) / breakdown.length
    const date = new Date()
    date.setDate(date.getDate() - index * 3)
    const photo = `https://i.pravatar.cc/96?img=${((index + 11) * 3) % 70 + 1}`

    return {
      id: `review-${index + 1}`,
      author,
      initials: author
        .split(' ')
        .map((part) => part[0])
        .join('')
        .slice(0, 2)
        .toUpperCase(),
      score,
      date: date.toISOString().slice(0, 10),
      comment: isNegative
        ? 'Много дублирования на лекциях, практики почти нет. Требования к зачёту держат в постоянном стрессе.'
        : 'Курс с практическими заданиями каждую неделю и подробной обратной связью. Преподаватель помогает увидеть точки роста.',
      tags: isNegative ? ['монотонно', 'нагрузка'] : index % 2 === 0 ? ['инновации', 'поддержка'] : ['структура', 'требовательность'],
      breakdown,
      photo
    }
  })
}

loadTeacherDirectory()
loadReviews()
loadUserReview()

const teacher = computed(() => {
  if (!props.teacherId) {
    return teacherDirectory.value[0] ?? null
  }
  return (
    teacherDirectory.value.find((item) => item.id === props.teacherId) ?? buildTeacherMock(props.teacherId)
  )
})

const teacherContacts = computed(() => {
  const contacts = teacher.value?.contacts ?? {}
  const items = []
  if (contacts.phone) {
    items.push({ key: 'phone', label: 'Телефон', value: contacts.phone })
  }
  if (contacts.email) {
    items.push({ key: 'email', label: 'Почта', value: contacts.email })
  }
  if (contacts.telegram) {
    items.push({ key: 'telegram', label: 'Telegram', value: contacts.telegram })
  }
  if (contacts.office) {
    items.push({ key: 'office', label: 'Аудитория', value: contacts.office })
  }
  if (contacts.site) {
    items.push({ key: 'site', label: 'Сайт', value: contacts.site })
  }
  return items
})

const userReview = computed(() => {
  if (!isAuthenticated.value || isBanned.value || user.value.role === 'admin') {
    return null
  }
  return userReviewSource.value
})

const userReviewVisible = ref(true)
const showDeleteModal = ref(false)

const confirmDelete = () => {
  userReviewSource.value = null
  showDeleteModal.value = false
  activeBreakdown.value = { id: null }
  userReviewCollapsed.value = false
}

const formatDate = (value) => {
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
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
  [...reviewsSource.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
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
}

.tag {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.16);
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
  padding: 26px 0 18px;
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
  background: rgba(15, 23, 42, 0.08);
  color: var(--color-muted);
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
