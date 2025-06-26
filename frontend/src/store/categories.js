// src/store/categories.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    list: [],       // список категорий
    loading: false,
    error: null
  }),

  actions: {
    async fetchCategories() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/categories')
        this.list = res.data  // ожидаем массив {id, name, description, slug}
      } catch (e) {
        this.error = 'Не удалось загрузить категории'
        console.error(e)
      } finally {
        this.loading = false
      }
    }
  }
})
