<template>
  <div class="search container">
    <section class="card search-panel">
      <h1>Поиск преподавателей</h1>
      <div class="filters">
        <label class="field">
          <span class="label">Фильтр по преподавателю</span>
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
        <div class="field sort-row">
          <label class="label">Сортировка по параметру</label>
          <div class="sort-controls">
            <select v-model="sortKey">
              <option value="rating">Средний балл</option>
              <option v-for="metric in metricDefinitions" :key="metric.key" :value="metric.key">
                {{ metric.label }}
              </option>
            </select>
            <button type="button" class="btn ghost" @click="toggleSortOrder">
              {{ sortOrder === 'desc' ? 'По убыванию' : 'По возрастанию' }}
            </button>
          </div>
        </div>
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
            <span v-for="tag in visibleTags(teacher.tagDetails)" :key="tag.id || tag.name" class="tag">
              #{{ tagLabel(tag) }} ({{ tag.count }})
            </span>
            <span v-if="hiddenCount(teacher.tagDetails)" class="tag muted">+{{ hiddenCount(teacher.tagDetails) }} ещё</span>
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
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PaginationControls from '../components/common/PaginationControls.vue'
import { api } from '../services/api'

const router = useRouter()

const searchQuery = ref('')
const selectedTags = ref([])
const sortKey = ref('rating')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = 12
const teacherCount = ref(0)

const availableTags = ref([])
const teachersRaw = ref([])
const resultsRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const metricDefinitions = [
  { key: 'overall', label: 'Общее впечатление' },
  { key: 'difficulty', label: 'Сложность' },
  { key: 'interesting', label: 'Интерес' },
  { key: 'responsibility', label: 'Организованность' },
  { key: 'fairness', label: 'Справедливость' }
]

const teachers = computed(() => teachersRaw.value)

const totalPages = computed(() => Math.max(1, Math.ceil(teacherCount.value / pageSize)))

const pagedResults = computed(() => teachers.value)

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
  void loadTeachers()
})

watch(sortKey, () => {
  currentPage.value = 1
  void loadTeachers()
})

const handleTagSelection = (event) => {
  const value = event.target.value
  if (value && !selectedTags.value.includes(value)) {
    selectedTags.value = [...selectedTags.value, value]
  }
  event.target.value = ''
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  void loadTeachers()
}

const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter((item) => item !== tagId)
}

const clearTags = () => {
  selectedTags.value = []
  void loadTeachers()
}

const tagLabel = (tag) => {
  if (tag && typeof tag === 'object') {
    return tag.name || tag.id
  }
  return availableTags.value.find((item) => item.id === tag)?.label ?? tag
}

const visibleTags = (tags = []) => tags.slice(0, 4)
const hiddenCount = (tags = []) => Math.max(0, tags.length - 4)

const openReviews = (teacher) => {
  router.push({ name: 'reviews', params: { teacherId: teacher.id } }).catch(() => {})
}

const handlePageChange = async (page) => {
  currentPage.value = page
  await loadTeachers()
  await nextTick()
  scrollResultsToTop()
}

const loadTags = async () => {
  try {
    const tags = await api.fetchTags()
    availableTags.value = tags.map((tag) => ({
      id: String(tag.id ?? tag.name),
      label: tag.name || tag.label || String(tag.id),
      count: tag.count ?? 0
    }))
  } catch (error) {
    console.warn('Не удалось загрузить теги', error)
  }
}

const mapTeacher = (entry) => {
  const metricsMap = entry.metrics || {}
  const metrics = metricDefinitions.map((metric) => ({
    key: metric.key,
    label: metric.label,
    score: Number(metricsMap[metric.key] ?? 0)
  }))

  const tagDetails = (entry.tags || []).map((tag) => ({
    id: String(tag.id ?? tag.name),
    name: tag.name || String(tag.id),
    count: tag.count ?? 0
  }))

  return {
    id: entry.id,
    isu: entry.isu,
    fullName: entry.name,
    staffId: entry.isu,
    rating: Number(entry.rating ?? 0),
    reviewCount: Number(entry.review_count ?? entry.reviewCount ?? 0),
    tags: tagDetails.map((tag) => tag.id),
    tagDetails,
    photo: entry.photo_url || 'https://via.placeholder.com/120x120.png?text=RS',
    metrics,
    metricsMap
  }
}

const loadTeachers = async () => {
  const fallbackMessage = 'Не удалось загрузить список преподавателей. Проверьте бэкенд.'
  try {
    const ordering = sortOrder.value === 'desc' ? `-${sortKey.value}` : sortKey.value
    const data = await api.fetchTeachers({
      page: currentPage.value,
      pageSize,
      search: searchQuery.value,
      tags: selectedTags.value,
      ordering
    })
    teachersRaw.value = (data?.results || []).map(mapTeacher)
    teacherCount.value = data?.count ?? teachersRaw.value.length
  } catch (error) {
    console.error(fallbackMessage, error)
    errorMessage.value = fallbackMessage
  }
}

const loadAll = async () => {
  loading.value = true
  await Promise.all([loadTags(), loadTeachers()])
  loading.value = false
}

onMounted(() => {
  void loadAll()
})
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

.sort-row {
  gap: 10px;
}

.sort-controls {
  display: flex;
  gap: 10px;
  align-items: center;
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
