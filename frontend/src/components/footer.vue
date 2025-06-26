<template>
  <footer class="footer">
    <div class="footer-container">
      <!-- Левая колонка: логотип и копирайт -->
      <div class="footer-left">
        <router-link to="/" class="footer-logo">
          МОРОЗНИК
        </router-link>
        <div class="footer-copy">2025 ALL RIGHTS RESERVED</div>
      </div>

      <!-- Центральная колонка: иконки соцсетей -->
      <div class="footer-center">
        <a
          href="https://t.me/yourchannel"
          class="social-icon"
          target="_blank"
          rel="noopener"
          aria-label="Telegram"
        >
          <!-- Telegram SVG -->
          <svg viewBox="0 0 240 240" fill="currentColor">
            <path
              d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm56.4 85.4l-21.8 102.8c-1.6 7.2-5.9 9-12 5.6l-33.2-24.4-16 15.4c-1.8 1.8-3.3 3.3-6.8 3.3l2.5-35.4 64.3-58.1c2.8-2.5-.6-3.9-4.4-1.4l-79.5 50.1-34.2-10.7c-7.4-2.3-7.5-7.4 1.6-11l133-51c6.1-2.3 11.4 1.4 9.3 10.7z"
            />
          </svg>
        </a>

        

        <a
          href="https://instagram.com/yourpage"
          class="social-icon"
          target="_blank"
          rel="noopener"
          aria-label="Instagram"
        >
          <!-- Instagram SVG -->
          <svg viewBox="0 0 512 512" fill="currentColor">
            <path
              d="M349.33 69.33H162.67C104.28 69.33 64 109.61 64 168v186.67c0 58.39 40.28 98.67 98.67 98.67h186.67c58.39 0 98.67-40.28 98.67-98.67V168c0-58.39-40.28-98.67-98.67-98.67zm64 284.67c0 35.29-28.71 64-64 64H162.67c-35.29 0-64-28.71-64-64V168c0-35.29 28.71-64 64-64h186.67c35.29 0 64 28.71 64 64v186.67z"
            />
            <path
              d="M256 149.33A106.67 106.67 0 1 0 362.67 256 106.79 106.79 0 0 0 256 149.33zm0 176A69.33 69.33 0 1 1 325.33 256 69.41 69.41 0 0 1 256 325.33z"
            />
            <circle cx="390.67" cy="121.33" r="21.33" />
          </svg>
        </a>
      </div>

      <!-- Правая колонка: служебные ссылки -->
      <div class="footer-right">
        <router-link to="/contacts">Контакты</router-link>
        <router-link to="/user-agreement">Соглашение пользователя</router-link>
        <router-link to="/privacy-policy">Политика конфиденциальности</router-link>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.footer {
  background-color: var(--background-color);
  color: var(--text-color);
  padding: 2rem 1rem;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-left,
.footer-center,
.footer-right {
  display: flex;
  align-items: center;
}

/* Левая колонка */
.footer-left {
  flex-direction: column;
  align-items: flex-start;
}
.footer-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  text-decoration: none;
  margin-bottom: 0.5rem;
}
.footer-copy {
  font-size: 0.85rem;
  opacity: 0.8;
}

/* Центр: иконки соцсетей */
.footer-center {
  gap: 1.5rem;
}
.social-icon {
  width: 32px;
  height: 32px;
  color: var(--text-color);
  transition: color 0.2s;
}
.social-icon:hover {
  color: var(--accent-color);
}

/* Правая колонка: ссылки */
.footer-right {
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}
.footer-right a {
  color: var(--text-color);
  text-decoration: none;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}
.footer-right a:hover {
  opacity: 0.7;
}
</style>
