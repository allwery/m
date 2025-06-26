<template>
  <div class="home">
    <!-- HERO -->
    <section ref="heroSection" class="hero-images">
      <div class="image" v-for="n in 3" :key="n">
        <img :src="`/img/mood${n}.jpg`" alt="mood" />
      </div>
    </section>

    <!-- MARQUEE -->
    <div class="marquee">
      <div class="marquee-content">
        <span v-for="n in 10" :key="n">
          Бесплатная доставка при заказе от 10 000₽
        </span>
      </div>
    </div>

    <!-- NEW ARRIVALS -->
    <section class="product-section">
      <h2>Новинки</h2>

      <div v-if="productsStore.loading" class="loader">Загрузка...</div>
      <p v-else-if="productsStore.error" class="error">{{ productsStore.error }}</p>
      <div v-else class="product-grid">
        <ProductCard
          v-for="product in productsStore.newItems"
          :key="product.id"
          :product="product"
          @select="goToProduct"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductsStore } from '@/store/products'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const productsStore = useProductsStore()
const heroSection = ref(null)
let observer = null

// Загрузка новинок
onMounted(() => {
  productsStore.fetchNewProducts(10)

  observer = new IntersectionObserver(
    ([entry]) => {
      const pct = entry.intersectionRatio
      if (heroSection.value) {
        heroSection.value.style.opacity = pct
        heroSection.value.style.transform = `translateY(${(1 - pct) * 100}px)`
      }
    },
    { threshold: Array.from({ length: 101 }, (_, i) => i / 100) }
  )
  if (heroSection.value) observer.observe(heroSection.value)
})

onBeforeUnmount(() => {
  if (observer && heroSection.value) observer.unobserve(heroSection.value)
})

function goToProduct(productId) {
  router.push({ name: 'ProductDetail', params: { productId } })
}
</script>

<style scoped>
.home {
  font-family: 'Inter', sans-serif;
  background: #121212;
  color: #fff;
  overflow-x: hidden;
}

/* HERO */
.hero-images {
  height: 100vh;
  display: flex;
  overflow: hidden;
  position: relative;
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.hero-images .image {
  flex: 1;
  overflow: hidden;
}
.hero-images img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* MARQUEE */
.marquee {
  overflow: hidden;
  background: #1a1a1a;
  border-top: 1px solid #333;
  border-bottom: 1px solid #333;
  padding: 0.5rem 0;
}
.marquee-content {
  display: flex;
  width: max-content;
  animation: scroll-left 15s linear infinite;
}
.marquee-content span {
  white-space: nowrap;
  font-size: 1.1rem;
  color: #ccc;
  padding-right: 4rem;
}
@keyframes scroll-left {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

/* PRODUCTS */
.product-section {
  padding: 4rem 2rem;
  text-align: center;
}
.product-section h2 {
  font-size: 2rem;
  margin-bottom: 2rem;
}
.loader, .error {
  color: #aaa;
  font-size: 1.2rem;
  margin: 2rem 0;
}
.product-grid {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(1.02); }
  to { opacity: 1; transform: scale(1); }
}
</style>
