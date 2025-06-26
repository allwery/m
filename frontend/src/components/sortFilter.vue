<template>
  <div class="controls">
    <!-- Поиск -->
    <input
      v-model="searchTerm"
      @input="emitFilters"
      type="text"
      placeholder="Поиск товара..."
      class="search-input"
    />

    <!-- Фильтр по категориям: стильные «pill» кнопки -->
    <div class="category-filters">
      <button
        v-for="cat in categoriesStore.list"
        :key="cat.id"
        :class="['pill', { active: selectedCategories.includes(cat.id) } ]"
        @click="toggleCategory(cat.id)"
      >
        {{ cat.name }}
      </button>
    </div>

    <!-- Сортировка -->
    <select v-model="sortOrder" @change="emitFilters" class="dropdown">
      <option value="asc">Сначала дешёвые</option>
      <option value="desc">Сначала дорогие</option>
    </select>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCategoriesStore } from '@/store/categories'

const emit = defineEmits(['update:filters'])
const categoriesStore = useCategoriesStore()

const searchTerm = ref('')
const selectedCategories = ref([])
const sortOrder = ref('asc')

function emitFilters() {
  emit('update:filters', {
    categories: [...selectedCategories.value],
    search:     searchTerm.value,
    sort:       sortOrder.value
  })
}

function toggleCategory(id) {
  const idx = selectedCategories.value.indexOf(id)
  if (idx === -1) {
    selectedCategories.value.push(id)
  } else {
    selectedCategories.value.splice(idx, 1)
  }
  emitFilters()
}

onMounted(async () => {
  if (!categoriesStore.list.length) {
    await categoriesStore.fetchCategories()
  }
  emitFilters()
})
</script>

<style scoped>
.controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input {
  background-color: #1e1e1e;
  color: #f0f0f0;
  border: 1px solid var(--accent-color);
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  min-width: 200px;
}
.search-input:hover {
  border-color: #fff;
}

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill {
  background: #2a2a2a;
  color: #ccc;
  border: 1px solid #444;
  border-radius: 1.5rem;
  padding: 0.4rem 1rem;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}
.pill.active {
  background-color: var(--accent-color);
  color: #1a1a1a;
  border-color: var(--accent-color);
}
.pill:hover {
  background-color: #444;
}

.dropdown {
  background-color: #1e1e1e;
  color: #f0f0f0;
  border: 1px solid var(--accent-color);
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  min-width: 160px;
}
.dropdown:hover {
  border-color: #fff;
}
</style>
