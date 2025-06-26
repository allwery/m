<template>
  <div class="cart-item">
    <img
      :src="item.image || placeholder"
      :alt="item.name"
      class="product-image"
    />
    <div class="info">
      <h3 class="title">{{ item.name }}</h3>
      <p class="size">Размер: {{ item.size.toUpperCase() }}</p>
      <p class="price">₽{{ item.price.toFixed(2) }}</p>
      <div class="quantity-controls">
        <button @click="decreaseQuantity" :disabled="item.quantity <= 1">−</button>
        <span>{{ item.quantity }}</span>
        <button @click="increaseQuantity">+</button>
      </div>
      <p class="line-total">Итого: ₽{{ lineTotal }}</p>
      <button class="remove" @click="removeItem">Удалить</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCartStore } from '@/store/cart'

const props = defineProps({
  item: {
    type: Object,
    required: true,
    // ожидаем поля: productId, name, price, image, quantity, size
  }
})

const cartStore = useCartStore()
const placeholder = '/img/placeholder.png'

// Локально считаем промежуточную сумму позиции
const lineTotal = computed(() =>
  (props.item.price * props.item.quantity).toFixed(2)
)

// Увеличить количество
async function increaseQuantity() {
  try {
    await cartStore.updateItem({
      product_id: props.item.productId,
      quantity:   props.item.quantity + 1,
      size:       props.item.size
    })
  } catch (err) {
    console.error('Не удалось увеличить количество', err)
  }
}

// Уменьшить количество
async function decreaseQuantity() {
  const newQty = props.item.quantity - 1
  if (newQty >= 1) {
    try {
      await cartStore.updateItem({
        product_id: props.item.productId,
        quantity:   newQty,
        size:       props.item.size
      })
    } catch (err) {
      console.error('Не удалось уменьшить количество', err)
    }
  }
}

// Удалить позицию из корзины
async function removeItem() {
  try {
    await cartStore.removeItem(props.item.productId)
  } catch (err) {
    console.error('Не удалось удалить позицию', err)
  }
}
</script>

<style scoped>
.cart-item {
  display: flex;
  align-items: center;
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
}
.cart-item:hover {
  transform: scale(1.02);
}
.product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 0.75rem;
  margin-right: 1rem;
}
.info {
  flex: 1;
}
.title {
  font-family: 'Inter', sans-serif;
  font-size: 1.2rem;
  margin: 0 0 0.5rem;
}
.price {
  font-size: 1rem;
  margin-bottom: 0.75rem;
}
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.quantity-controls button {
  background-color: #333;
  color: #fff;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: background 0.2s;
  cursor: pointer;
}
.quantity-controls button:disabled {
  opacity: 0.5;
  cursor: default;
}
.quantity-controls button:hover:not(:disabled) {
  background-color: #555;
}
.line-total {
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
}
.remove {
  background-color: transparent;
  border: none;
  color: #e57373;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.2s;
}
.remove:hover {
  color: #ef5350;
}
</style>
