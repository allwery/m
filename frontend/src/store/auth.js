// src/store/auth.js
import { defineStore } from 'pinia'
import api from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  id: 'auth',
  state: () => ({
    accessToken: localStorage.getItem('token'),
    user:        JSON.parse(localStorage.getItem('user') || 'null')
  }),
  actions: {
    async login(email, password) {
      const res = await api.post('/auth/login', { email, password })
      this.accessToken = res.data.token
      this.user        = res.data.user

      localStorage.setItem('token', this.accessToken)
      localStorage.setItem('user', JSON.stringify(this.user))

      return this.user
    },

    async register(email, password) {
      const res = await api.post('/auth/register', { email, password })
      this.accessToken = res.data.token
      this.user        = res.data.user

      localStorage.setItem('token', this.accessToken)
      localStorage.setItem('user', JSON.stringify(this.user))

      return this.user
    },

    logout() {
      this.accessToken = null
      this.user        = null

      localStorage.removeItem('token')
      localStorage.removeItem('user')

      router.replace({ name: 'Login' })
    },

    /**
     * Подгрузить свежие данные профиля (используется после изменений)
     */
    async fetchUserProfile() {
      if (!this.accessToken) return
      try {
        const res = await api.get('/auth/me', {
          headers: { Authorization: `Bearer ${this.accessToken}` }
        })
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (err) {
        console.error('Не удалось обновить профиль', err)
      }
    }
  }
})
