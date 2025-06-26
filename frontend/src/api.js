// src/api.js
import axios from 'axios'
import router from './router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.replace({ name: 'Login' })
    }
    return Promise.reject(err)
  }
)

export default api
