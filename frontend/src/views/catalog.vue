<template>
  <div class="catalog animate-fade-in">
    <h1 class="title">Каталог товаров</h1>

    <SortFilter @update:filters="productsStore.setFilters" />

    <div v-if="productsStore.loading" class="loader">
      Загрузка товаров...
    </div>
    <p v-else-if="productsStore.error" class="error-message">
      {{ productsStore.error }}
    </p>

    <transition-group name="fade-up" tag="div" class="grid">
      <ProductCard
        v-for="(product, index) in productsStore.items"
        :key="product.id"
        :product="product"
        :style="{ animationDelay: `${index * 100}ms` }"
        @select="goToProduct"
      />
    </transition-group>

    <button
      type="button"
      v-if="!productsStore.loading && productsStore.currentPage < productsStore.pages"
      class="load-more"
      @click="productsStore.loadMore"
    >
      Загрузить ещё
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useProductsStore } from '@/store/products'
import ProductCard from '@/components/productCard.vue'
import SortFilter from '@/components/sortFilter.vue'

const router = useRouter()
const productsStore = useProductsStore()

// при монтировании загружаем первые товары
productsStore.fetchProducts()

function goToProduct(productId) {
  router.push({ name: 'productDetail', params: { productId } })
}
</script>

<style scoped>
.catalog {
  padding: 2rem;
  background-color: #121212;
  min-height: 100vh;
  color: #f0f0f0;
  font-family: 'Inter', sans-serif;
}

.title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 2rem;
  color: var(--accent-color);
}

.loader,
.error-message {
  text-align: center;
  font-size: 1.2rem;
  color: #aaa;
  margin: 2rem 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.load-more {
  display: block;
  margin: 2rem auto;
  padding: 0.75rem 1.5rem;
  background: #444;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.3s;
}
.load-more:hover {
  background: #666;
}

.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.5s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.animate-fade-in {
  animation: fadeIn 0.5s ease forwards;
  opacity: 0;
}
@keyframes fadeIn {
  to { opacity: 1; }
}
</style>
