<template>
  <div class="cart animate-fade-in">
    <h1 class="cart-title">Ваша корзина</h1>

    <div v-if="cartStore.loading" class="loader">
      Загрузка корзины...
    </div>

    <div v-else-if="!cartStore.items.length" class="empty-cart">
      <p>Корзина пуста...</p>
      <router-link to="/catalog" class="back-button">
        Перейти в каталог
      </router-link>
    </div>

    <div v-else class="cart-list">
      <!-- CartItem сам вызывает cartStore.updateItem и cartStore.removeItem -->
      <CartItem
        v-for="item in cartStore.items"
        :key="item.id"
        :item="item"
      />

      <div class="cart-total">
        <p>
          Общая сумма:
          <strong>{{ totalPrice }} ₽</strong>
        </p>
        <button
          class="checkout-button"
          @click="goToCheckout"
        >
          Оформить заказ
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import CartItem from '@/components/cartItem.vue'

const router    = useRouter()
const cartStore = useCartStore()

onMounted(() => {
  cartStore.fetchCart()
})

const totalPrice = computed(() =>
  cartStore.items.reduce((sum, item) => sum + item.lineTotal, 0).toFixed(2)
)

function goToCheckout() {
  router.push({ name: 'Checkout' })
}
</script>

<style scoped>
.cart {
  background-color: #1a1a1a;
  color: #f5f5f5;
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  min-height: 100vh;
}
.cart-title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 2rem;
  color: var(--accent-color);
}
.loader {
  text-align: center;
  color: #aaa;
  font-size: 1.2rem;
  margin-top: 2rem;
}
.empty-cart {
  text-align: center;
  font-size: 1.3rem;
  color: #ccc;
}
.back-button {
  margin-top: 1rem;
  display: inline-block;
  color: #1a1a1a;
  background: #ffffff;
  padding: 0.6rem 1.4rem;
  border-radius: 2rem;
  text-decoration: none;
  transition: background 0.3s;
}
.back-button:hover {
  background: #ffffff;
}
.cart-list {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.cart-total {
  text-align: right;
  margin-top: 2rem;
  font-size: 1.3rem;
}
.checkout-button {
  margin-top: 1rem;
  background-color: #888;
  color: #1a1a1a;
  border: none;
  padding: 0.8rem 1.5rem;
  font-size: 1.1rem;
  border-radius: 2rem;
  cursor: pointer;
  transition: background 0.3s ease;
}
.checkout-button:hover:not(:disabled) {
  background-color: #fff;
}
</style>
