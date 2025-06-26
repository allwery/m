// src/store/orders.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useOrdersStore = defineStore('orders', {
  state: () => ({
    myOrders: [],        // заказы текущего пользователя
    allOrders: [],       // все заказы для админа
    currentOrder: null,  // детали выбранного заказа
    loading: false,
    error: null
  }),

  actions: {
    // Загрузить заказы пользователя
    async fetchMyOrders() {
      this.loading = true
      this.error   = null
      try {
        const res = await api.get('/orders')
        this.myOrders = res.data
      } catch (e) {
        this.error = 'Не удалось загрузить ваши заказы'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Загрузить все заказы (для админа)
    async fetchAllOrders() {
      this.loading = true
      this.error   = null
      try {
        const res = await api.get('/admin/orders')
        this.allOrders = res.data
      } catch (e) {
        this.error = 'Не удалось загрузить заказы'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Загрузить детали одного заказа
    async fetchOrderDetail(orderId) {
      this.loading = true
      this.error   = null
      try {
        const res = await api.get(`/orders/${orderId}`)
        this.currentOrder = res.data
      } catch (e) {
        this.error = 'Не удалось загрузить детали заказа'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    // Создать заказ (с учётом реферального кода и списания баллов)
    async createOrder({
      shipping_street,
      shipping_city,
      shipping_postal_code,
      shipping_country,
      shipping_method,
      shipping_cost,
      referral_code,
      use_points
    }) {
      this.loading = true
      this.error   = null
      try {
        await api.post('/orders', {
          shipping_street,
          shipping_city,
          shipping_postal_code,
          shipping_country,
          shipping_method,
          shipping_cost,
          // новые поля
          referral_code,
          use_points
        })
      } catch (e) {
        // объединяем ошибки от сервера или показываем общее сообщение
        this.error = e.response?.data?.errors?.join('; ')
                   || e.response?.data?.error
                   || 'Ошибка при создании заказа'
        throw e
      } finally {
        this.loading = false
      }
    }
  }
})
