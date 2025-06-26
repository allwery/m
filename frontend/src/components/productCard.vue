<template>
  <div class="card-wrapper" @click="goToDetail">
    <div class="card">
      <img
        :src="primaryImageUrl"
        :alt="product.name"
        class="image"
        loading="lazy"
        @error="onImgError"
      />
      <div class="info">
        <h2 class="title">{{ product.name }}</h2>
        <p class="price">₽{{ formatPrice(product.price) }}</p>
      </div>
      <button class="go-btn" @click.stop="goToDetail">
        Перейти к товару
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  product: { type: Object, required: true }
})
const router = useRouter()
const placeholder = '/img/placeholder.jpg'

const images = computed(() => props.product.images || [])
const primaryImageUrl = computed(() => {
  if (images.value.length) {
    const primary = images.value.find(i => i.is_primary) || images.value[0]
    return primary.url
  }
  return placeholder
})

function goToDetail() {
  router.push({
    name: 'productDetail',
    params: { productId: props.product.id }
  })
}

function onImgError(e) {
  e.target.src = placeholder
}

function formatPrice(val) {
  return Number(val).toLocaleString('ru-RU')
}
</script>

<style scoped>
.card-wrapper {
  display: block;
  width: 100%;
  cursor: pointer;
}

.card {
  background-color: #121212;
  border: 1px solid #444;
  border-radius: 1.5rem;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(255,255,255,0.1);
}

.image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.info {
  padding: 0.8rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.title {
  font-size: 1.1rem;
  color: #fff;
  margin: 0;
}

.price {
  font-size: 1rem;
  color: #ccc;
  margin: 0;
}

.go-btn {
  margin: 0.8rem 1rem;
  padding: 0.5rem;
  background-color: #444;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.go-btn:hover {
  background-color: #666;
}
</style>
