// src/store/users.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useUsersStore = defineStore('users', {
  state: () => ({
    list: [],       // список пользователей
    loading: false,
    error: null
  }),

  actions: {
    async fetchAllUsers() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/admin/users')
        this.list = res.data
      } catch (e) {
        this.error = 'Не удалось загрузить пользователей'
        console.error(e)
      } finally {
        this.loading = false
      }
    }
  }
})
