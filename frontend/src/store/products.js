// src/store/products.js
import { defineStore } from 'pinia'
import api from '@/api'

export const AVAILABLE_SIZES = ['s', 'm', 'l', 'xl']

export const useProductsStore = defineStore('products', {
  id: 'products',
  state: () => ({
    // Основной каталог
    items: [],          // загруженные товары
    total: 0,           // общее число товаров
    pages: 0,           // число страниц
    currentPage: 1,     // текущая страница
    perPage: 12,        // элементов на страницу

    // Новинки
    newItems: [],       // последние добавленные товары

    // Фильтры
    filters: {
      categories: [],   // массив id категорий
      search: '',       // поисковая строка
      sort: 'asc'       // 'asc' | 'desc'
    },

    // Состояние загрузки / ошибки
    loading: false,
    error: null
  }),

  actions: {
    /**
     * Загрузить страницу каталога (заменяет items)
     * @param {number} page — номер страницы
     */
    async fetchProducts(page = 1) {
      this.loading = true
      this.error = null
      try {
        const params = {
          page,
          per_page: this.perPage,
          sort: this.filters.sort
        }
        // Фильтрация по категориям
        if (this.filters.categories.length) {
          params.category_id = this.filters.categories.join(',')
        }
        // Поиск
        if (this.filters.search) {
          params.search = this.filters.search
        }

        const res = await api.get('/products', { params })
        this.items = res.data.products
        this.total = res.data.total
        this.pages = res.data.pages
        this.currentPage = res.data.current_page
      } catch (e) {
        console.error(e)
        this.error = 'Не удалось загрузить товары'
      } finally {
        this.loading = false
      }
    },

    /**
     * Загрузить "Новинки" — последние добавленные товары
     * @param {number} limit — сколько новинок взять
     */
    async fetchNewProducts(limit = 10) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/products/new', { params: { limit } })
        this.newItems = res.data
      } catch (e) {
        console.error(e)
        this.error = 'Не удалось загрузить новинки'
      } finally {
        this.loading = false
      }
    },

    /**
     * Дозагрузить следующую страницу каталога (append)
     */
    async loadMore() {
      if (this.currentPage >= this.pages) return
      this.loading = true
      this.error = null
      const nextPage = this.currentPage + 1

      try {
        const params = {
          page: nextPage,
          per_page: this.perPage,
          sort: this.filters.sort
        }
        if (this.filters.categories.length) {
          params.category_id = this.filters.categories.join(',')
        }
        if (this.filters.search) {
          params.search = this.filters.search
        }

        const res = await api.get('/products', { params })
        this.items = [...this.items, ...res.data.products]
        this.currentPage = res.data.current_page
      } catch (e) {
        console.error(e)
        this.error = 'Не удалось загрузить ещё товары'
      } finally {
        this.loading = false
      }
    },

    /**
     * Установить новые фильтры и перезагрузить каталог с первой страницы
     */
    setFilters({ categories, search, sort }) {
      this.filters = { categories, search, sort }
      this.currentPage = 1
      this.fetchProducts(1)
    }
  }
})
