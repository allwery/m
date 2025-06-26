<template>
  <header class="header">
    <nav class="nav">
      <router-link to="/" class="logo">
        <img src="/img/logo.png" alt="Moroznik" class="logo-img" />
      </router-link>
      <div class="icons">
        <router-link to="/catalog" class="icon">
          <i class="fas fa-th-large"></i>
        </router-link>
        <router-link to="/cart" class="icon">
          <i class="fas fa-shopping-bag"></i>
        </router-link>
        <router-link v-if="!authStore.accessToken" to="/login" class="icon">
          <i class="fas fa-user"></i>
        </router-link>
        <router-link v-else to="/profile" class="icon">
          <i class="fas fa-user-circle"></i>
        </router-link>
        <button v-if="authStore.accessToken" @click="authStore.logout" class="icon logout-btn">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const router = useRouter()

// После logout стор перенаправляет на Login, но чтобы вернуть на главную:
function logout() {
  authStore.logout()
  router.push({ name: 'Home' })
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

.header {
  background: #111;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-img {
  height: 3rem;
  width: auto;
  display: block;
}

.icons {
  display: flex;
  gap: 1.2rem;
  align-items: center;
}

.icon {
  color: #ddd;
  font-size: 1.2rem;
  transition: color 0.3s ease;
  text-decoration: none;
}

.icon:hover {
  color: #fff;
}

.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
}
</style>
