<template>
  <div class="pagination">
    <button
      type="button"
      class="pager-btn"
      :disabled="currentPage <= 1"
      @click="setPage(currentPage - 1)"
    >
      Назад
    </button>

    <div class="pagination-status">
      <span>Страница</span>
      <input
        v-model.number="inputValue"
        type="number"
        min="1"
        :max="totalPages"
        @keyup.enter="commitInput"
        @blur="commitInput"
      />
      <span>из {{ totalPages }}</span>
    </div>

    <button
      type="button"
      class="pager-btn"
      :disabled="currentPage >= totalPages"
      @click="setPage(currentPage + 1)"
    >
      Вперед
    </button>
  </div>
</template>

<script setup>
/* global defineProps, defineEmits */
import { ref, watch } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:currentPage'])

const inputValue = ref(props.currentPage)

watch(
  () => props.currentPage,
  (value) => {
    inputValue.value = value
  }
)

const clamp = (value) => {
  const min = 1
  const max = props.totalPages || 1
  if (Number.isNaN(value)) {
    return props.currentPage
  }
  return Math.min(Math.max(value, min), max)
}

const setPage = (value) => {
  const next = clamp(value)
  if (next !== props.currentPage) {
    emit('update:currentPage', next)
  }
}

const commitInput = () => {
  setPage(Number(inputValue.value))
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.pagination-status {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: var(--color-muted);
}

.pagination-status input {
  width: 64px;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  font-weight: 600;
  text-align: center;
}

.pager-btn {
  border: none;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  cursor: pointer;
  transition: background 0.2s ease;
}

.pager-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.24);
}

.pager-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
