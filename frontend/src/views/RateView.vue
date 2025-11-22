<template>
  <div class="rate container">
    <form class="card form" @submit.prevent="handleSubmit">
      <header class="form-header">
        <h1>Оставьте подробный отзыв</h1>
        <p>Расскажите о своём опыте по нескольким параметрам, чтобы помочь студентам и администрации.</p>
        <p v-if="prefillNotice" class="prefill-notice">{{ prefillNotice }}</p>
      </header>

      <div class="grid">
        <label class="field">
          <span class="label">Преподаватель (поиск по ФИО или табельному номеру)</span>
          <input
            v-model="form.teacherQuery"
            list="teacher-options"
            placeholder="Начните вводить имя или номер"
            @change="syncTeacher"
          />
          <datalist id="teacher-options">
            <option v-for="option in teacherOptions" :key="option.id" :value="option.display"></option>
          </datalist>
        </label>

        <label class="field">
          <span class="label">Учебный год</span>
          <select v-model="form.studyYear" required>
            <option value="" disabled>Выберите год</option>
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </label>

        <label class="field">
          <span class="label">Дисциплина</span>
          <input v-model="form.subject" type="text" placeholder="Например, линейная алгебра" required />
        </label>

        <label class="field">
          <span class="label">Комментарий (0-2000 символов)</span>
          <textarea
            v-model="form.comment"
            :maxlength="commentLimit"
            rows="6"
            placeholder="Что особенно запомнилось в работе преподавателя?"
          ></textarea>
          <span class="note" :class="{ warn: commentTooLong }">
            {{ form.comment.length }}/{{ commentLimit }}
          </span>
        </label>
      </div>

      <section class="ratings">
        <h2>Оцените каждый параметр</h2>
        <div class="rating-grid">
          <div v-for="scale in ratingScales" :key="scale.key" class="rating-row">
            <div class="rating-label">
              <span>{{ scale.label }}</span>
              <small>{{ scale.hint }}</small>
            </div>
            <div class="rating-control">
              <input
                v-model.number="form.ratings[scale.key]"
                type="range"
                min="1"
                max="5"
                step="1"
              />
              <div class="ticks">
                <span v-for="n in 5" :key="n">{{ n }}</span>
              </div>
            </div>
            <div class="rating-value">{{ form.ratings[scale.key] }}</div>
          </div>
        </div>
      </section>

      <section class="tags">
        <h2>Добавьте теги</h2>
        <p class="hint">Выберите подходящие теги или добавьте новый. Допустимы 1-32 символа: строчные буквы, цифры, "-" или "_".</p>
        <div class="tag-options">
          <label v-for="tag in availableTags" :key="tag" class="tag-option">
            <input
              type="checkbox"
              :value="tag"
              v-model="form.tags"
            />
            <span>#{{ tag }}</span>
          </label>
        </div>
        <div class="new-tag">
          <input v-model="newTag" type="text" placeholder="Добавить новый тег" list="tag-suggestions" />
          <datalist id="tag-suggestions">
            <option v-for="tag in tagSuggestions" :key="tag" :value="tag"></option>
          </datalist>
          <button type="button" class="btn ghost" @click="addNewTag">Добавить</button>
        </div>
        <p v-if="tagError" class="error">{{ tagError }}</p>
      </section>

      <footer class="form-footer">
        <button type="submit" class="btn primary" :disabled="submitting">
          {{ submitting ? 'Отправляем...' : 'Опубликовать отзыв' }}
        </button>
        <p v-if="formError" class="error">{{ formError }}</p>
        <p v-if="success" class="success">Сохранили! Скоро перейдём к отзывам...</p>
      </footer>
    </form>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUserReviewMock } from '../mocks/userReview'

const route = useRoute()
const router = useRouter()

const commentLimit = 2000

const teacherOptions = ref([])
const years = ref([])
const ratingScales = ref([])
const availableTags = ref([])
const existingReviewSnapshot = ref(null)

const loadTeacherOptions = () => {
  teacherOptions.value = getTeacherOptionsMock()
}

const loadYears = () => {
  years.value = getAcademicYearsMock()
}

const loadRatingScales = () => {
  ratingScales.value = getRatingScalesMock()
}

const loadAvailableTags = () => {
  availableTags.value = getAvailableTagsMock()
}

const loadExistingReviewSnapshot = () => {
  existingReviewSnapshot.value = getUserReviewMock()
}

const getTeacherOptionsMock = () => [
  { id: 't-1', display: 'Преподаватель 1 (ID1000)' },
  { id: 't-2', display: 'Преподаватель 2 (ID1001)' },
  { id: 't-3', display: 'Преподаватель 3 (ID1002)' },
  { id: 't-4', display: 'Преподаватель 4 (ID1003)' }
]

const getAcademicYearsMock = () => ['2025/2026', '2024/2025', '2023/2024', '2022/2023']

const getRatingScalesMock = () => [
  { key: 'overall', label: 'Общее впечатление', hint: '1 — плохо, 5 — отлично' },
  { key: 'difficulty', label: 'Сложность', hint: '1 — легко, 5 — очень сложно' },
  { key: 'engagement', label: 'Интерес', hint: '1 — скучно, 5 — вдохновляет' },
  { key: 'organization', label: 'Организация', hint: '1 — хаотично, 5 — структурировано' },
  { key: 'fairness', label: 'Справедливость', hint: '1 — непонятно, 5 — прозрачно' }
]

const getAvailableTagsMock = () => ['инновации', 'поддержка', 'требовательность', 'исследования', 'наставничество', 'практика']

loadTeacherOptions()
loadYears()
loadRatingScales()
loadAvailableTags()
loadExistingReviewSnapshot()

const form = reactive({
  teacherId: '',
  teacherQuery: '',
  studyYear: '',
  subject: '',
  comment: '',
  ratings: {
    overall: 3,
    difficulty: 3,
    engagement: 3,
    organization: 3,
    fairness: 3
  },
  tags: []
})

const newTag = ref('')
const tagError = ref('')
const formError = ref('')
const submitting = ref(false)
const success = ref(false)
const prefillNotice = ref('')
const prefilledTeacherId = ref('')

const tagSuggestions = computed(() =>
  availableTags.value.filter((tag) => !form.tags.includes(tag))
)

const commentTooLong = ref(false)
watch(
  () => form.comment,
  (value) => {
    commentTooLong.value = value.length > commentLimit
  }
)

const ensureTagsInOptions = (tags = []) => {
  if (!Array.isArray(tags) || !tags.length) {
    return
  }
  const unique = new Set(availableTags.value)
  let changed = false
  tags.forEach((tag) => {
    if (!unique.has(tag)) {
      unique.add(tag)
      changed = true
    }
  })

  if (changed) {
    availableTags.value = Array.from(unique)
  }
}

const findExistingReview = (teacherId) => {
  if (!teacherId) {
    return null
  }
  const snapshot = existingReviewSnapshot.value
  if (snapshot && snapshot.teacherId === teacherId) {
    return snapshot
  }
  return null
}

const applyExistingReview = (review) => {
  if (!review) {
    return
  }

  form.studyYear = review.studyYear ?? form.studyYear
  form.subject = review.subject ?? form.subject
  form.comment = review.comment ?? form.comment
  ensureTagsInOptions(review.tags)
  form.tags = Array.from(new Set(review.tags ?? []))

  ratingScales.value.forEach((scale) => {
    const value = review.ratings?.[scale.key]
    if (typeof value === 'number' && !Number.isNaN(value)) {
      form.ratings[scale.key] = value
    }
  })

  prefilledTeacherId.value = review.teacherId
  prefillNotice.value = 'Мы нашли ваш предыдущий отзыв и подставили значения. Обновите их при необходимости.'
}

const resetPrefillNotice = () => {
  prefilledTeacherId.value = ''
  prefillNotice.value = ''
}

const teacherFromQuery = route.query.teacherId
if (typeof teacherFromQuery === 'string' && teacherFromQuery) {
  form.teacherId = teacherFromQuery
  const option = teacherOptions.value.find((item) => item.id === teacherFromQuery)
  if (option) {
    form.teacherQuery = option.display
  }
}

watch(
  () => route.query.teacherId,
  (value) => {
    if (typeof value === 'string') {
      form.teacherId = value
      const option = teacherOptions.value.find((item) => item.id === value)
      form.teacherQuery = option ? option.display : value
    }
  }
)

watch(
  () => form.teacherId,
  (value) => {
    if (!value) {
      resetPrefillNotice()
      return
    }

    const review = findExistingReview(value)
    if (review) {
      applyExistingReview(review)
    } else if (prefilledTeacherId.value) {
      resetPrefillNotice()
    }
  },
  { immediate: true }
)

const syncTeacher = () => {
  const query = form.teacherQuery.trim().toLowerCase()
  if (!query) {
    form.teacherId = ''
    return
  }

  const match = teacherOptions.value.find((item) => {
    const displayLower = item.display.toLowerCase()
    if (displayLower === query) {
      return true
    }

    const idLower = item.id.toLowerCase()
    if (idLower === query) {
      return true
    }

    const staffMatch = item.display.match(/\(([^)]+)\)/)
    if (staffMatch && staffMatch[1].toLowerCase() === query) {
      return true
    }

    return false
  })

  if (match) {
    form.teacherId = match.id
    form.teacherQuery = match.display
  } else {
    form.teacherId = ''
  }
}

const addNewTag = () => {
  const trimmed = newTag.value.trim()
  if (!trimmed) {
    tagError.value = 'Введите тег перед добавлением.'
    return
  }

  const normalized = trimmed.toLowerCase()
  const pattern = /^[a-zа-яё0-9-_]{1,32}$/u
  if (!pattern.test(normalized)) {
    tagError.value = 'Тег должен содержать 1-32 символа: строчные буквы, цифры, "-" или "_".'
    return
  }

  if (!availableTags.value.includes(normalized)) {
    availableTags.value = [...availableTags.value, normalized]
  }

  if (!form.tags.includes(normalized)) {
    form.tags = [...form.tags, normalized]
  }

  newTag.value = ''
  tagError.value = ''
}

const handleSubmit = () => {
  formError.value = ''
  if (!form.teacherId) {
    syncTeacher()
    if (!form.teacherId) {
      formError.value = 'Выберите преподавателя из списка перед отправкой.'
      return
    }
  }

  submitting.value = true
  success.value = false

  setTimeout(() => {
    submitting.value = false
    success.value = true

    setTimeout(() => {
      router.push({ name: 'reviews', params: { teacherId: form.teacherId } }).catch(() => {})
    }, 1200)
  }, 1100)
}
</script>

<style scoped>
.rate {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form {
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-header h1 {
  margin: 0;
  color: var(--color-text);
}

.form-header p {
  margin: 8px 0 0;
  color: var(--color-muted);
  max-width: 600px;
}

.prefill-notice {
  margin: 12px 0 0;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  font-weight: 600;
}

:global([data-theme='dark']) .prefill-notice {
  background: rgba(96, 165, 250, 0.22);
  color: #dbeafe;
}

.grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
  color: var(--color-muted);
}

.field input,
.field select,
.field textarea {
  padding: 12px 16px;
  padding-right: 40px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  font-weight: 500;
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

.field textarea {
  resize: vertical;
}

.note {
  font-size: 13px;
  align-self: flex-end;
  color: var(--color-muted);
}

.note.warn {
  color: var(--color-warning);
}

.ratings {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.rating-grid {
  display: grid;
  gap: 18px;
}

.rating-row {
  display: grid;
  grid-template-columns: 220px 1fr 60px;
  gap: 18px;
  align-items: center;
}

.rating-label span {
  font-weight: 600;
  color: var(--color-text);
}

.rating-label small {
  display: block;
  font-size: 12px;
  color: var(--color-muted);
}

.rating-control input[type='range'] {
  width: 100%;
}

.ticks {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-muted);
  margin-top: 4px;
}

.rating-value {
  font-weight: 700;
  color: var(--color-primary);
  font-size: 18px;
}

.tags {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hint {
  margin: 0;
  color: var(--color-muted);
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  font-weight: 600;
}

.tag-option input {
  accent-color: var(--color-primary);
}

.new-tag {
  display: flex;
  gap: 12px;
  align-items: center;
}

.new-tag input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

.error {
  color: var(--color-error);
  margin: 0;
}

.form-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}


.form-footer .btn {
  min-width: 160px;
}

.success {
  margin: 0;
  color: var(--color-success);
  font-weight: 600;
}

@media (max-width: 900px) {
  .form {
    padding: 28px;
  }

  .rating-row {
    grid-template-columns: 1fr;
  }
}
</style>
