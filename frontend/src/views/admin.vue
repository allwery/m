<template>
  <div class="admin-container animate-fade-in">
    <Header />
    <div class="admin-content">
      <h1 class="title">Админ-панель</h1>

      <section class="block">
        <h2>Пользователи</h2>
        <div v-if="usersStore.loading" class="loader">Загрузка пользователей...</div>
        <p v-else-if="usersStore.error" class="error-message">{{ usersStore.error }}</p>
        <ul v-else>
          <li v-for="user in usersStore.list" :key="user.id">
            {{ user.email }} — {{ user.is_admin ? 'admin' : 'user' }}
          </li>
        </ul>
      </section>

      <section class="block">
        <h2>Заказы</h2>
        <div v-if="ordersStore.loading" class="loader">Загрузка заказов...</div>
        <p v-else-if="ordersStore.error" class="error-message">{{ ordersStore.error }}</p>
        <ul v-else>
          <li v-for="order in ordersStore.allOrders" :key="order.id">
            Заказ #{{ order.id }}: {{ order.status }} — {{ order.total_amount }} ₽
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Header from '@/components/header.vue'
import { useUsersStore } from '@/store/users'
import { useOrdersStore } from '@/store/orders'

const usersStore = useUsersStore()
const ordersStore = useOrdersStore()

onMounted(() => {
  usersStore.fetchAllUsers()
  ordersStore.fetchAllOrders()
})
</script>

<style scoped>
.admin-container {
  background: #111;
  color: #fff;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-top: 5rem;
  display: flex;
  justify-content: center;
}
.admin-content {
  width: 90%;
  max-width: 800px;
  background: #222;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 0 10px rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.block {
  background: #333;
  padding: 1rem;
  border-radius: 0.75rem;
}
.block h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #444;
}
li:last-child {
  border-bottom: none;
}
.loader {
  text-align: center;
  color: #aaa;
  font-size: 1.1rem;
  margin: 1rem 0;
}
.error-message {
  color: #f66;
  text-align: center;
  margin: 1rem 0;
}
.title {
  font-size: 2rem;
  text-align: center;
}
.animate-fade-in {
  animation: fadeIn 1s ease forwards;
  opacity: 0;
}
@keyframes fadeIn {
  to { opacity: 1; }
}
</style>
