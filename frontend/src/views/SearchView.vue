<template>
  <div class="search container">
    <section class="card search-panel">
      <h1>Поиск преподавателей</h1>
      <div class="filters">
        <label class="field">
          <span class="label">Фильтр по ФИО или табельному номеру</span>
          <input v-model="searchQuery" type="text" placeholder="Начните вводить ФИО или табельный номер" />
        </label>
        <label class="field">
          <span class="label">Фильтр по тегам</span>
          <select @change="handleTagSelection">
            <option value="">Выберите тег</option>
            <option v-for="tag in availableTags" :key="tag.id" :value="tag.id">
              {{ tag.label }} ({{ tag.count }})
            </option>
          </select>
        </label>
        <label class="field">
          <span class="label">Сортировка по параметру</span>
          <select v-model="sortKey">
            <option value="rating">Средний балл</option>
            <option v-for="metric in metricDefinitions" :key="metric.key" :value="metric.key">
              {{ metric.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="active-tags" v-if="selectedTags.length">
        <span class="active-title">Выбранные теги:</span>
        <button
          v-for="tagId in selectedTags"
          :key="tagId"
          type="button"
          class="tag-chip"
          @click="removeTag(tagId)"
        >
          {{ tagLabel(tagId) }} ×
        </button>
        <button type="button" class="reset" @click="clearTags">Сбросить теги</button>
      </div>
    </section>

    <section ref="resultsRef" class="results">
      <div class="grid" role="list">
        <article v-for="teacher in pagedResults" :key="teacher.id" class="card teacher-card" role="listitem">
          <div class="card-top">
            <img :src="teacher.photo" :alt="teacher.fullName" />
            <div class="meta">
              <h2>{{ teacher.fullName }}</h2>
              <div class="staff-id">Табельный номер: {{ teacher.staffId }}</div>
              <div class="rating">Средний рейтинг: {{ teacher.rating.toFixed(1) }}</div>
            </div>
          </div>
          <div class="metrics-block">
            <div v-for="metric in teacher.metrics" :key="metric.key" class="metric-row">
              <div class="metric-header">
                <span class="metric-label">{{ metric.label }}</span>
                <span class="metric-score">{{ metric.score.toFixed(1) }}</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: metric.score * 20 + '%' }"></div>
              </div>
            </div>
          </div>
          <div class="tag-row">
            <span v-for="tag in visibleTags(teacher.tags)" :key="tag" class="tag">#{{ tagLabel(tag) }}</span>
            <span v-if="hiddenCount(teacher.tags)" class="tag muted">+{{ hiddenCount(teacher.tags) }} ещё</span>
          </div>
          <button type="button" class="btn primary open-btn" @click="openReviews(teacher)">
            Открыть отзывы
          </button>
        </article>
      </div>

      <p v-if="!pagedResults.length" class="empty">
        По заданным условиям никого не нашли. Попробуйте изменить запрос или фильтры по тегам.
      </p>

      <PaginationControls
        v-if="totalPages > 1"
        :current-page="currentPage"
        :total-pages="totalPages"
        @update:currentPage="handlePageChange"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PaginationControls from '../components/common/PaginationControls.vue'

const router = useRouter()

const searchQuery = ref('')
const selectedTags = ref([])
const sortKey = ref('rating')
const currentPage = ref(1)
const pageSize = 18

const availableTags = ref([])
const teachers = ref([])
const resultsRef = ref(null)

const loadAvailableTags = () => {
  availableTags.value = getAvailableTagsMock()
}

const loadTeachers = () => {
  teachers.value = getTeachersMock()
}

const getAvailableTagsMock = () => [
  { id: 'innovative', label: 'инновации', count: 28 },
  { id: 'supportive', label: 'поддержка', count: 35 },
  { id: 'demanding', label: 'требовательность', count: 12 },
  { id: 'clear', label: 'понятные объяснения', count: 41 },
  { id: 'research', label: 'наука и исследования', count: 16 },
  { id: 'mentor', label: 'наставничество', count: 19 }
]

const metricDefinitions = [
  { key: 'overall', label: 'Общее впечатление' },
  { key: 'difficulty', label: 'Сложность' },
  { key: 'engagement', label: 'Интерес' },
  { key: 'organization', label: 'Организация' },
  { key: 'fairness', label: 'Справедливость' }
]

const getTeachersMock = () => {
  const tagIds = getAvailableTagsMock().map((tag) => tag.id)
  return Array.from({ length: 48 }, (_, index) => {
    const shuffled = [...tagIds].sort(() => 0.5 - Math.random())
    const tagCount = 3 + (index % 4)
    const metrics = metricDefinitions.map((definition, metricIndex) => {
      const seed = 3.1 + ((index * 7 + metricIndex * 3) % 14) / 10
      const clipped = Math.min(4.9, Math.max(2.6, seed))
      return {
        key: definition.key,
        label: definition.label,
        score: clipped
      }
    })

    const averageScore = metrics.reduce((acc, metric) => acc + metric.score, 0) / metrics.length
    const metricsMap = metrics.reduce((acc, metric) => {
      acc[metric.key] = metric.score
      return acc
    }, {})

    return {
      id: `t-${index + 1}`,
      fullName: `Преподаватель ${index + 1}`,
      staffId: `ID${String(1000 + index)}`,
      rating: averageScore,
      tags: shuffled.slice(0, tagCount),
      photo: `https://i.pravatar.cc/120?img=${(index % 70) + 1}`,
      metrics,
      metricsMap
    }
  })
}

loadAvailableTags()
loadTeachers()

const queryParts = computed(() => searchQuery.value.trim().toLowerCase().split(/\s+/).filter(Boolean))

const filteredResults = computed(() => {
  return teachers.value.filter((teacher) => {
    const matchesQuery = queryParts.value.length
      ? queryParts.value.some((part) =>
          teacher.fullName.toLowerCase().includes(part) || teacher.staffId.toLowerCase().includes(part)
        )
      : true

    const matchesTags = selectedTags.value.length
      ? selectedTags.value.every((tagId) => teacher.tags.includes(tagId))
      : true

    return matchesQuery && matchesTags
  })
})

const getSortValue = (teacher, key) => {
  if (key === 'rating') {
    return teacher.rating
  }
  return teacher.metricsMap?.[key] ?? 0
}

const sortedResults = computed(() => {
  const key = sortKey.value
  return [...filteredResults.value].sort((a, b) => {
    const diff = getSortValue(b, key) - getSortValue(a, key)
    if (diff !== 0) {
      return diff
    }
    return a.fullName.localeCompare(b.fullName)
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedResults.value.length / pageSize)))

const pagedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedResults.value.slice(start, start + pageSize)
})

const scrollResultsToTop = () => {
  if (typeof window === 'undefined' || !resultsRef.value) {
    return
  }
  const rect = resultsRef.value.getBoundingClientRect()
  const top = rect.top + window.scrollY - 120
  window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' })
}

watch([searchQuery, selectedTags], () => {
  currentPage.value = 1
})

watch(sortKey, () => {
  currentPage.value = 1
})

const handleTagSelection = (event) => {
  const value = event.target.value
  if (value && !selectedTags.value.includes(value)) {
    selectedTags.value = [...selectedTags.value, value]
  }
  event.target.value = ''
}

const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter((item) => item !== tagId)
}

const clearTags = () => {
  selectedTags.value = []
}

const tagLabel = (tagId) => {
  return availableTags.value.find((tag) => tag.id === tagId)?.label ?? tagId
}

const visibleTags = (tags) => tags.slice(0, 4)
const hiddenCount = (tags) => Math.max(0, tags.length - 4)

const openReviews = (teacher) => {
  router.push({ name: 'reviews', params: { teacherId: teacher.id } }).catch(() => {})
}

const handlePageChange = async (page) => {
  currentPage.value = page
  await nextTick()
  scrollResultsToTop()
}
</script>

<style scoped>
.search {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.search-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-panel h1 {
  margin: 0;
  color: var(--color-text);
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
  color: var(--color-muted);
}

.field input,
.field select {
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  font-weight: 500;
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

.active-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.active-title {
  font-weight: 600;
  color: var(--color-text);
}

.tag-chip {
  padding: 8px 14px;
  border-radius: 999px;
  border: none;
  background: rgba(59, 130, 246, 0.16);
  color: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
}

.tag-chip:hover {
  background: rgba(59, 130, 246, 0.24);
}

.reset {
  background: transparent;
  border: none;
  color: var(--color-muted);
  text-decoration: underline;
  cursor: pointer;
}

.results {
  display: flex;
  flex-direction: column;
}

.teacher-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
}

.card-top {
  display: flex;
  gap: 16px;
}

.card-top img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.meta h2 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text);
}

.staff-id {
  font-size: 13px;
  color: var(--color-muted);
}

.rating {
  font-weight: 600;
  color: var(--color-primary);
}

.metrics-block {
  display: grid;
  gap: 10px;
}

.metric-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.metric-label {
  color: var(--color-muted);
  font-weight: 600;
}

.metric-score {
  font-weight: 700;
  color: var(--color-primary);
}

.metric-bar {
  height: 6px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.tag-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.16);
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
}

.tag.muted {
  background: rgba(15, 23, 42, 0.08);
  color: var(--color-muted);
}

.open-btn {
  margin-top: auto;
  align-self: flex-start;
}

.empty {
  text-align: center;
  color: var(--color-muted);
  margin: 32px 0;
}

@media (max-width: 1180px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
