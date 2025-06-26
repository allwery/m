<template>
  <div class="app">
    <Header />

    <main class="main">
      <RouterView />
    </main>

    <!-- Показываем Footer, если у текущего роута нет meta.hideFooter -->
    <Footer v-if="!route.meta.hideFooter" />
  </div>
</template>

<script setup>
import Header from './components/header.vue'
import Footer from './components/footer.vue'
import { RouterView, useRoute } from 'vue-router'

const route = useRoute()
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

:root {
  --background-color: #121212;
  --text-color: #f0f0f0;
  --accent-color: #ffffff;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* --- Mobile-first base styles --- */

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main {
  flex: 1;
  padding: 1rem;              /* уменьшенный отступ для мобильных */
  animation: fadeIn 0.6s ease;
}

/* --- Tablet и десктоп (>=768px) --- */
@media (min-width: 768px) {
  .main {
    padding: 2rem;            /* исходный отступ для больших экранов */
  }
}

/* --- Широкие экраны (>=1024px) --- */
@media (min-width: 1024px) {
  .main {
    padding: 3rem;            /* можно увеличить отступ ещё больше */
  }
}

/* Анимация */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

