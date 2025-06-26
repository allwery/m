<template>
  <div class="checkout-container animate-fade-in">
    <div class="checkout-content">
      <h1 class="title">Оформление заказа</h1>

      <!-- Сводка заказа -->
      <div class="order-summary" v-if="cartStore.items.length">
        <h2>Ваш заказ</h2>
        <ul>
          <li v-for="item in cartStore.items" :key="item.id">
            <div class="item-info">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-size"> Размер: {{ item.size.toUpperCase() }}</span>
            </div>
            <span class="item-details">
              {{ item.quantity }} шт. — ₽{{ item.lineTotal.toFixed(2) }}
            </span>
          </li>
        </ul>
        <div class="summary-total">
          <strong>Сумма товаров: ₽{{ subtotal }}</strong>
        </div>
      </div>

      <form @submit.prevent="submitOrder" class="checkout-form">
        <h2 class="section-title">Информация о доставке</h2>
        <input v-model="street" type="text" placeholder="Улица и номер дома" required />
        <input v-model="city" type="text" placeholder="Город" required />
        <input v-model="postalCode" type="text" placeholder="Почтовый индекс" required />

        <h2 class="section-title">Способ доставки</h2>
        <select v-model="shippingMethod">
          <option value="pochta">Почта России</option>
          <option value="cdek">СДЭК</option>
        </select>

        <p class="shipping-cost">
          Стоимость доставки: <strong>₽{{ shippingCost }}</strong>
        </p>

        <!-- Реферальный код -->
        <h2 class="section-title">Реферальный код</h2>
        <input
          v-model="referralCode"
          type="text"
          placeholder="Введите код (необязательно)"
        />

        <!-- Баллы пользователя -->
        <h2 class="section-title">Использовать баллы</h2>
        <p>Ваш баланс: {{ authStore.user.points_balance }} баллов</p>
        <input
          v-model.number="usePoints"
          type="number"
          :max="authStore.user.points_balance"
          min="0"
          placeholder="Сколько баллов списать"
        />

        <div class="summary-total">
          <strong>Итог к оплате: ₽{{ finalTotal }}</strong>
        </div>

        <button
          type="submit"
          class="confirm-button"
          :disabled="orderStore.loading"
        >
          {{ orderStore.loading ? 'Оформление...' : 'Подтвердить заказ' }}
        </button>

        <p v-if="orderStore.error" class="error-message">{{ orderStore.error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { useOrdersStore } from '@/store/orders'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const router      = useRouter()
const cartStore   = useCartStore()
const orderStore  = useOrdersStore()
const authStore   = useAuthStore()

// Адрес
const street           = ref('')
const city             = ref('')
const postalCode       = ref('')
const shippingMethod   = ref('pochta')

// Реферальный код и баллы
const referralCode     = ref('')
const usePoints        = ref(0)

// Подгруженные адреса (необязательно)
const addresses        = ref([])

const shippingCost = computed(() =>
  shippingMethod.value === 'cdek' ? 300 : 200
)

const subtotal = computed(() =>
  cartStore.items.reduce((sum, item) => sum + item.lineTotal, 0).toFixed(2)
)

const finalTotal = computed(() => {
  const total = parseFloat(subtotal.value) + shippingCost.value - usePoints.value
  return total > 0 ? total.toFixed(2) : '0.00'
})

async function fetchAddresses() {
  try {
    const res = await api.get('/user/addresses')
    addresses.value = res.data
    const addr = addresses.value.find(a => a.is_default) || addresses.value[0]
    if (addr) {
      street.value     = addr.street
      city.value       = addr.city
      postalCode.value = addr.postal_code || addr.postalCode
    }
  } catch (err) {
    console.error('Не удалось загрузить адреса:', err)
  }
}

onMounted(() => {
  cartStore.fetchCart()
  fetchAddresses()
})

async function submitOrder() {
  orderStore.error = null

  try {
    // 1) Создаём заказ
    await orderStore.createOrder({
      shipping_street:      street.value.trim(),
      shipping_city:        city.value.trim(),
      shipping_postal_code: postalCode.value.trim(),
      shipping_country:     'Россия',
      shipping_method:      shippingMethod.value,
      shipping_cost:        shippingCost.value,
      referral_code:        referralCode.value.trim() || undefined,
      use_points:           usePoints.value
    })

    // 2) Обновляем профиль пользователя (баллы, и т.д.)
    await authStore.fetchUserProfile()

    // 3) Очищаем корзину
    await cartStore.clearCart()

    // 4) Переходим в профиль, сразу на таб "orders"
    router.push({ name: 'Profile', query: { tab: 'orders' } })

  } catch (e) {
    // orderStore.error уже содержит сообщение от сервера
  }
}
</script>

<style scoped>
.checkout-container {
  background: #111;
  color: #fff;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-top: 5rem;
  display: flex;
  justify-content: center;
}
.checkout-content {
  width: 360px;
  background: #222;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}
.title {
  font-size: 2rem;
  margin-bottom: 1rem;
  text-align: center;
  color: var(--accent-color);
}
.order-summary {
  background: #1e1e1e;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}
.order-summary h2 {
  font-size: 1.3rem;
  margin-bottom: 0.75rem;
  color: var(--accent-color);
}
.order-summary ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.order-summary li {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #333;
}
.order-summary li:last-child {
  border-bottom: none;
}
.summary-total {
  text-align: right;
  margin-top: 0.75rem;
  font-size: 1rem;
}
.section-title {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  color: var(--accent-color);
}
.checkout-form input,
.checkout-form select {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  background: #333;
  color: #fff;
  margin-bottom: 0.75rem;
}
.shipping-cost {
  text-align: right;
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #aaa;
}
/* Стили для реферального кода и баллов */
.checkout-form input[type="text"],
.checkout-form input[type="number"] {
  background: #2a2a2a;
  border: 1px solid #444;
}
.checkout-form input[type="text"]::placeholder,
.checkout-form input[type="number"]::placeholder {
  color: #777;
}
/* Подписи баллов и кода */
.checkout-form p {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: #ccc;
}
.confirm-button {
  width: 100%;
  padding: 0.75rem;
  background: #888;
  color: #1a1a1a;
  font-weight: bold;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.3s;
}
.confirm-button:hover:not(:disabled) {
  background: #fff;
}
.confirm-button:disabled {
  opacity: 0.6;
  cursor: default;
}
.error-message {
  color: #f66;
  text-align: center;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.animate-fade-in {
  animation: fadeIn 0.6s ease forwards;
  opacity: 0;
}
@keyframes fadeIn {
  to { opacity: 1; }
}
</style>
