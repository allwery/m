// src/store/reviews.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useReviewsStore = defineStore('reviews', {
  state: () => ({
    list: [],        // список отзывов для текущего продукта
    loading: false,  // флаг загрузки (для любых операций)
    error: null      // строка ошибки
  }),

  actions: {
    // Загрузить отзывы для конкретного товара
    async fetchReviews(productId) {
      this.loading = true
      this.error   = null
      try {
        const res = await api.get('/reviews', { params: { product_id: productId } })
        this.list = res.data
      } catch (e) {
        // если сервер вернул массив ошибок — объединяем их, иначе общее сообщение
        this.error = e.response?.data?.errors?.join('; ') || 'Не удалось загрузить отзывы.'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Отправить новый отзыв
    async postReview({ product_id, rating, comment }) {
      this.loading = true
      this.error   = null
      try {
        await api.post('/reviews', { product_id, rating, comment })
        // после успешного POST — обновляем список
        await this.fetchReviews(product_id)
      } catch (e) {
        this.error = e.response?.data?.errors?.join('; ') || 'Не удалось отправить отзыв.'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Обновить существующий отзыв
    async updateReview({ reviewId, product_id, rating, comment }) {
      this.loading = true
      this.error   = null
      try {
        await api.put(`/reviews/${reviewId}`, { rating, comment })
        await this.fetchReviews(product_id)
      } catch (e) {
        this.error = e.response?.data?.errors?.join('; ') || 'Не удалось обновить отзыв.'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Удалить отзыв
    async deleteReview({ reviewId, product_id }) {
      this.loading = true
      this.error   = null
      try {
        await api.delete(`/reviews/${reviewId}`)
        await this.fetchReviews(product_id)
      } catch (e) {
        this.error = e.response?.data?.errors?.join('; ') || 'Не удалось удалить отзыв.'
        console.error(e)
      } finally {
        this.loading = false
      }
    }
  }
})
