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
          <template v-if="!useCustomSubject">
            <input
              v-model="form.subjectQuery"
              list="subject-options"
              placeholder="Например, линейная алгебра"
              @change="syncSubject"
            />
            <datalist id="subject-options">
              <option v-for="option in subjectOptions" :key="option.id" :value="option.name"></option>
            </datalist>
          </template>
          <template v-else>
            <input
              v-model="customSubject"
              placeholder="Введите название дисциплины"
            />
          </template>
          <button type="button" class="btn ghost small" @click="toggleCustomSubject">
            {{ useCustomSubject ? 'Выбрать из списка' : 'Ввести свою дисциплину' }}
          </button>
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
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { api } from '../services/api'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated } = useAuthStore()

const commentLimit = 2000

const teacherOptions = ref([])
const subjectOptions = ref([])
const useCustomSubject = ref(false)
const customSubject = ref('')
const years = ref([])
const ratingScales = ref([
  { key: 'overall', label: 'Общее впечатление', hint: '1 — плохо, 5 — отлично' },
  { key: 'difficulty', label: 'Сложность', hint: '1 — сложно, 5 — очень легко' },
  { key: 'interesting', label: 'Интерес', hint: '1 — скучно, 5 — вдохновляет' },
  { key: 'responsibility', label: 'Организация', hint: '1 — хаотично, 5 — структурировано' },
  { key: 'fairness', label: 'Справедливость', hint: '1 — непонятно, 5 — прозрачно' }
])
const availableTags = ref([])
const existingReviewSnapshot = ref(null)

const form = reactive({
  teacherIsu: '',
  teacherQuery: '',
  subjectId: '',
  subjectQuery: '',
  studyYear: '',
  comment: '',
  ratings: {
    overall: 3,
    difficulty: 3,
    interesting: 3,
    responsibility: 3,
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
const prefilledTeacherIsu = ref('')

const tagSuggestions = computed(() => availableTags.value.filter((tag) => !form.tags.includes(tag)))

const commentTooLong = ref(false)
watch(
  () => form.comment,
  (value) => {
    commentTooLong.value = value.length > commentLimit
  }
)

const loadTeacherOptions = async (search = '') => {
  try {
    // запрашиваем больше элементов, чтобы покрыть выборку из страницы отзывов
    const page = await api.fetchTeachers({ page: 1, pageSize: 200, search })
    const list = Array.isArray(page) ? page : page?.results || []
    teacherOptions.value = list.map((item) => ({
      id: item.id,
      isu: item.isu,
      display: `${item.name} (${item.isu})`
    }))
  } catch (error) {
    console.warn('Не удалось загрузить преподавателей', error)
  }
}

const loadSubjectOptions = async () => {
  try {
    const response = await api.client.get('/api/subjects/')
    const subjects = Array.isArray(response.data) ? response.data : response.data?.results || []
    subjectOptions.value = subjects.map((subject) => ({ id: subject.id, name: subject.name }))
  } catch (error) {
    console.warn('Не удалось загрузить список дисциплин (возможно, требуется доступ администратора)', error)
  }
}

const loadYears = () => {
  const current = new Date().getFullYear()
  years.value = [current + 1, current, current - 1, current - 2]
}

const loadAvailableTags = async () => {
  try {
    const tags = await api.fetchTags()
    availableTags.value = tags.map((tag) => tag.name || tag.label || String(tag.id))
  } catch (error) {
    console.warn('Не удалось загрузить теги', error)
  }
}

const loadExistingReviewSnapshot = async (teacherIsu) => {
  if (!teacherIsu || !isAuthenticated.value) {
    existingReviewSnapshot.value = null
    return
  }
  try {
    const page = await api.fetchReviews({ teacherIsu })
    const match = (page?.results || []).find((review) => review.owner === user.value.username)
    existingReviewSnapshot.value = match || null
  } catch (error) {
    console.warn('Не удалось получить предыдущий отзыв', error)
    existingReviewSnapshot.value = null
  }
}

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

const applyExistingReview = (review) => {
  if (!review) {
    return
  }

  form.studyYear = review.study_year ?? form.studyYear
  form.comment = review.comment ?? form.comment
  ensureTagsInOptions(review.tags)
  form.tags = Array.from(new Set(review.tags ?? []))

  if (review.subject) {
    const match = subjectOptions.value.find((subject) => String(subject.id) === String(review.subject))
    if (match) {
      form.subjectId = match.id
      form.subjectQuery = match.name
      useCustomSubject.value = false
      customSubject.value = ''
    } else {
      form.subjectId = ''
      useCustomSubject.value = true
      customSubject.value = review.subject_name || form.subjectQuery || ''
    }
  }

  ratingScales.value.forEach((scale) => {
    const value = review[scale.key]
    if (typeof value === 'number' && !Number.isNaN(value)) {
      form.ratings[scale.key] = value
    }
  })

  prefilledTeacherIsu.value = review.teacher
  prefillNotice.value = 'Мы нашли ваш предыдущий отзыв и подставили значения. Обновите их при необходимости.'
}

const resetPrefillNotice = () => {
  prefilledTeacherIsu.value = ''
  prefillNotice.value = ''
}

const syncTeacher = () => {
  const query = form.teacherQuery.trim().toLowerCase()
  if (!query) {
    form.teacherIsu = ''
    return
  }

  const match = teacherOptions.value.find((item) => {
    const displayLower = item.display.toLowerCase()
    if (displayLower === query) return true
    if (String(item.isu).toLowerCase() === query) return true
    if (String(item.id).toLowerCase() === query) return true
    return false
  })

  if (match) {
    form.teacherIsu = String(match.isu)
    form.teacherQuery = match.display
    void loadExistingReviewSnapshot(match.isu).then((review) => {
      if (review) {
        applyExistingReview(review)
      } else if (prefilledTeacherIsu.value) {
        resetPrefillNotice()
      }
    })
  } else {
    form.teacherIsu = ''
  }
}

const syncSubject = () => {
  const query = form.subjectQuery.trim().toLowerCase()
  if (!query) {
    form.subjectId = ''
    if (!useCustomSubject.value) {
      customSubject.value = ''
    }
    return
  }

  const match = subjectOptions.value.find((subject) => {
    if (subject.name.toLowerCase() === query) return true
    if (String(subject.id).toLowerCase() === query) return true
    return false
  })

  if (match) {
    form.subjectId = match.id
    form.subjectQuery = match.name
    useCustomSubject.value = false
    customSubject.value = ''
  } else {
    form.subjectId = ''
    // allow switching to custom when not found
    customSubject.value = form.subjectQuery
  }
}

const toggleCustomSubject = () => {
  useCustomSubject.value = !useCustomSubject.value
  if (useCustomSubject.value) {
    customSubject.value = form.subjectQuery || customSubject.value
    form.subjectId = ''
  } else {
    customSubject.value = ''
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

const handleSubmit = async () => {
  formError.value = ''
  if (!form.teacherIsu) {
    syncTeacher()
    if (!form.teacherIsu) {
      formError.value = 'Выберите преподавателя из списка перед отправкой.'
      return
    }
  }

  if (!form.subjectId && !customSubject.value.trim()) {
    syncSubject()
    if (!form.subjectId && !customSubject.value.trim()) {
      formError.value = 'Выберите дисциплину из списка или введите свою.'
      return
    }
  }

  submitting.value = true
  success.value = false

  const payload = {
    teacher: form.teacherIsu,
    subject: form.subjectId || customSubject.value.trim(),
    study_year: Number(form.studyYear),
    comment: form.comment,
    overall: Number(form.ratings.overall),
    difficulty: Number(form.ratings.difficulty),
    interesting: Number(form.ratings.interesting),
    responsibility: Number(form.ratings.responsibility),
    fairness: Number(form.ratings.fairness),
    tags: [...form.tags]
  }

  try {
    const editing =
      existingReviewSnapshot.value &&
      String(existingReviewSnapshot.value.teacher) === String(form.teacherIsu) &&
      existingReviewSnapshot.value.id

    if (editing) {
      await api.updateReview(existingReviewSnapshot.value.id, payload)
    } else {
      await api.createReview(payload)
    }
    success.value = true
    const teacherOption = teacherOptions.value.find((option) => String(option.isu) === String(form.teacherIsu))
    const teacherId = teacherOption?.id || form.teacherIsu
    setTimeout(() => {
      router.push({ name: 'reviews', params: { teacherId } }).catch(() => {})
    }, 800)
  } catch (error) {
    console.error('Не удалось сохранить отзыв', error)
    const apiMessage = error?.response?.data?.detail || error?.response?.data?.non_field_errors?.[0]
    formError.value = apiMessage || 'Не удалось сохранить отзыв. Проверьте данные и попробуйте снова.'
  } finally {
    submitting.value = false
  }
}

const initialize = async () => {
  loadYears()
  await Promise.all([loadTeacherOptions(), loadSubjectOptions(), loadAvailableTags()])

  const teacherFromQuery = route.query.teacherId
  if (typeof teacherFromQuery === 'string' && teacherFromQuery) {
    let option = teacherOptions.value.find(
      (item) => String(item.id) === teacherFromQuery || String(item.isu) === teacherFromQuery
    )

    if (!option) {
      try {
        const teacherData = await api.fetchTeacher(teacherFromQuery)
        option = {
          id: teacherData.id,
          isu: teacherData.isu,
          display: `${teacherData.name} (${teacherData.isu})`
        }
        teacherOptions.value = [...teacherOptions.value, option]
      } catch (error) {
        console.warn('Не удалось найти преподавателя для автоподстановки', error)
      }
    }

    if (option) {
      form.teacherIsu = String(option.isu)
      form.teacherQuery = option.display
      await loadExistingReviewSnapshot(option.isu)
      if (existingReviewSnapshot.value) {
        applyExistingReview(existingReviewSnapshot.value)
      }
    }
  }
}

onMounted(() => {
  void initialize()
})

watch(
  () => route.query.teacherId,
  async (value) => {
    if (typeof value === 'string' && value) {
      let option = teacherOptions.value.find(
        (item) => String(item.id) === value || String(item.isu) === value
      )

      if (!option) {
        try {
          const teacherData = await api.fetchTeacher(value)
          option = {
            id: teacherData.id,
            isu: teacherData.isu,
            display: `${teacherData.name} (${teacherData.isu})`
          }
          teacherOptions.value = [...teacherOptions.value, option]
        } catch (error) {
          console.warn('Не удалось найти преподавателя для автоподстановки', error)
        }
      }

      if (option) {
        form.teacherIsu = String(option.isu)
        form.teacherQuery = option.display
        await loadExistingReviewSnapshot(option.isu)
        if (existingReviewSnapshot.value) {
          applyExistingReview(existingReviewSnapshot.value)
        } else {
          resetPrefillNotice()
        }
      }
    }
  }
)
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
