<template>
  <div class="auth-container animate-fade-in">
    <form @submit.prevent="handleLogin" class="auth-form">
      <h1 class="title">Вход</h1>

      <!-- Поле для email -->
      <input
        v-model="email"
        type="email"
        placeholder="Email"
        required
      />
      <!-- Поле для пароля -->
      <input
        v-model="password"
        type="password"
        placeholder="Пароль"
        required
      />

      <button type="submit" :disabled="loading">
        {{ loading ? 'Входим...' : 'Войти' }}
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>

      <router-link to="/register" class="switch-link">
        Нет аккаунта? Зарегистрируйтесь
      </router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore }          from '@/store/auth'
import Header                     from '@/components/Header.vue'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref(null)

async function handleLogin() {
  loading.value = true
  error.value   = null

  try {
    await auth.login(email.value.trim(), password.value)

    // Тут токен уже точно в localStorage
    console.log('token после login:', localStorage.getItem('token'))

    router.push(route.query.redirect || { name: 'Profile' })
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось войти'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  background: #111;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 5rem;
  font-family: 'Inter', sans-serif;
}

.auth-form {
  background: #222;
  padding: 2rem;
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 1rem;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
}

.auth-form input,
.auth-form button {
  padding: 0.75rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.5rem;
}

.auth-form button {
  background: #444;
  color: #fff;
  cursor: pointer;
  transition: background 0.3s ease;
}

.auth-form button:disabled {
  opacity: 0.6;
  cursor: default;
}

.auth-form button:hover:not(:disabled) {
  background: #666;
}

.switch-link {
  color: #aaa;
  font-size: 0.9rem;
  text-align: center;
  text-decoration: underline;
}

.title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}

.error-message {
  color: #f66;
  text-align: center;
  font-size: 0.9rem;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease forwards;
  opacity: 0;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}
</style>
