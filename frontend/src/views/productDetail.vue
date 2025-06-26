<template>
  <div class="product-detail animate-fade-in">
    <div v-if="loading" class="loader">Загрузка товара...</div>
    <p v-else-if="error" class="error-message">{{ error }}</p>

    <template v-else>
      <!-- Lightbox Overlay -->
      <div v-if="lightboxOpen" class="lightbox" @click.self="closeLightbox">
        <button class="close-btn" @click="closeLightbox">✕</button>
        <button class="nav prev" @click.stop="prevImage">‹</button>
        <img :src="images[currentIndex]" class="lightbox-image" />
        <button class="nav next" @click.stop="nextImage">›</button>
        <div class="lightbox-thumbs">
          <img
            v-for="(url, idx) in images"
            :key="idx"
            :src="url"
            :class="{ active: idx === currentIndex }"
            @click="goToImage(idx)"
          />
        </div>
      </div>

      <!-- Галерея изображений -->
      <div class="image-section">
        <div class="main-image">
          <img
            :src="selectedImage"
            class="product-image"
            loading="lazy"
            @click="openLightbox"
            @error="onImgError"
          />
        </div>
        <div class="thumbnails">
          <img
            v-for="(url, idx) in images"
            :key="idx"
            :src="url"
            :class="['thumb', { active: idx === currentIndex }]"
            loading="lazy"
            @click="goToImage(idx)"
            @error="onImgError"
          />
        </div>
      </div>

      <!-- Информация о товаре и добавление в корзину -->
      <div class="info-section">
        <h2 class="title">{{ product.name }}</h2>
        <p class="price">₽{{ formatPrice(product.price) }}</p>
        <p class="description" v-html="formattedDescription"></p>

        <div class="size-selector">
          <label for="size-select">Размер:</label>
          <select id="size-select" v-model="selectedSize">
            <option disabled value="">Выберите размер</option>
            <option
              v-for="s in AVAILABLE_SIZES"
              :key="s"
              :value="s"
            >
              {{ s.toUpperCase() }}
            </option>
          </select>
        </div>

        <button
          class="add-to-cart"
          @click="addToCart"
          :disabled="cartStore.loading "
        >
          {{ cartStore.loading ? 'Добавление...' : 'Добавить в корзину' }}
        </button>

        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </div>

      <!-- Окно отзывов -->
      <div class="reviews-section">
          <h3>Отзывы</h3>
          
          <!-- Загрузка -->
          <p v-if="reviewsStore.loading" class="loader-small">Загрузка отзывов…</p>
          
          <!-- Ошибка -->
          <p v-else-if="reviewsStore.error" class="error-message">
            {{ reviewsStore.error }}
          </p>
          
          <!-- Контейнер с отзывами -->
          <div v-else class="reviews-container">
            <div v-if="!reviewsStore.list.length" class="no-reviews">
              Пока нет отзывов.
            </div>

            <!-- Форма нового отзыва -->
            <div v-if="userLoggedIn && !hasUserReview" class="new-review-form">
              <h4>Оставить отзыв</h4>
              <!-- Ошибка формы -->
              <p v-if="reviewsStore.error" class="error-message">
                {{ reviewsStore.error }}
              </p>
              <div class="form-group">
                <label>Оценка:</label>
                <select v-model="newReview.rating">
                  <option disabled value="">Выберите рейтинг</option>
                  <option v-for="i in 5" :key="i" :value="i">{{ i }} ★</option>
                </select>
              </div>
              <div class="form-group">
                <label>Комментарий:</label>
                <textarea
                  v-model="newReview.comment"
                  rows="3"
                  placeholder="Ваш комментарий"
                ></textarea>
              </div>
              <button class="btn-submit-review" @click="createReview" :disabled="submittingReview">Отправить</button>
              
            </div>

            <!-- Список отзывов -->
            <div
              v-for="r in reviewsStore.list"
              :key="r.id"
              class="review-card"
            >
              <div class="review-header">
                <span class="review-user">{{ r.username || 'Аноним' }}</span>
                <span class="review-rating">
                  <template v-for="i in 5">
                    <span v-if="i <= r.rating">★</span><span v-else>☆</span>
                  </template>
                </span>
              </div>

              <div v-if="editId === r.id" class="edit-form">
                <div class="form-group">
                  <label>Рейтинг:</label>
                  <select v-model="editReview.rating">
                    <option disabled value="">Выберите рейтинг</option>
                    <option v-for="i in 5" :key="i" :value="i">{{ i }} ★</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Комментарий:</label>
                  <textarea v-model="editReview.comment" rows="3"></textarea>
                </div>
                <button @click="updateReview" :disabled="submittingReview">Сохранить</button>
                <button @click="cancelEdit" class="btn-cancel">Отмена</button>
              </div>
              <div v-else>
                <p v-if="r.comment" class="review-comment">{{ r.comment }}</p>
                <small class="review-date">{{ new Date(r.created_at).toLocaleDateString() }}</small>
              </div>

              <div
                v-if="userLoggedIn && (r.user_id === currentUserId || isAdmin)"
                class="review-actions"
              >
                <button v-if="editId !== r.id" @click="startEdit(r)">Редактировать</button>
                <button @click="deleteReview(r.id)" class="btn-delete">Удалить</button>
              </div>
            </div>
          </div>
        </div>

      <!-- Рекомендуемые товары -->
      <div class="recommendations-section">
        <h3>Также заказывают</h3>
        <div class="recommendations">
          <RouterLink
            v-for="item in recommendations"
            :key="item.id"
            :to="{ name: 'productDetail', params: { productId: item.id } }"
            class="recommend-link"
          >
            <ProductCard :product="item" />
         </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import { useReviewsStore } from '@/store/reviews'
import ProductCard from '@/components/productCard.vue'
import { AVAILABLE_SIZES } from '@/store/products'

const route      = useRoute()
const router     = useRouter()
const cartStore  = useCartStore()
const authStore  = useAuthStore()
const reviewsStore = useReviewsStore()

// User info
const currentUserId = computed(() => authStore.user?.id || null)
const isAdmin       = computed(() => !!authStore.user?.is_admin)
const userLoggedIn  = computed(() => !!authStore.user)

// Product state
const product        = ref({})
const images         = ref([])
const selectedImage  = ref('')
const currentIndex   = ref(0)
const lightboxOpen   = ref(false)
const selectedSize   = ref(AVAILABLE_SIZES[0] || '')
const recommendations= ref([])
const loading        = ref(false)
const error          = ref(null)
const successMessage = ref(null)

// Review helpers
const hasUserReview = computed(() =>
  reviewsStore.list.some(r => r.user_id === currentUserId.value)
)

// New/Edit
const newReview      = ref({ rating: '', comment: '' })
const editId         = ref(null)
const editReview     = ref({ rating: '', comment: '' })
const submittingReview = ref(false)

const placeholder    = '/img/placeholder.jpg'

async function loadProduct() {
  loading.value = true
  error.value   = null
  try {
    const { data: prod } = await api.get(`/products/${route.params.productId}`)
    product.value = prod

    images.value = prod.images.map(img => img.url)
    if (!images.value.length) images.value = [placeholder]
    selectedImage.value = images.value[0]
    currentIndex.value = 0
    selectedSize.value  = AVAILABLE_SIZES[0] || ''

    const { data: list } = await api.get('/products', { params: { per_page: 8 } })
    recommendations.value = list.products
      .filter(p => p.id !== prod.id)
      .sort(() => Math.random() - 0.5)
      .slice(0, 4)

    // <-- здесь вызываем Pinia-стор вместо локальной функции
    await reviewsStore.fetchReviews(prod.id)
  } catch {
    error.value = 'Не удалось загрузить данные о товаре.'
  } finally {
    loading.value = false
  }
}

// Теперь локальную функцию loadReviews можно удалить

// Создание отзыва
async function createReview() {
  if (!newReview.value.rating) return
  submittingReview.value = true
  try {
    await reviewsStore.postReview({
      product_id: product.value.id,
      rating:     newReview.value.rating,
      comment:    newReview.value.comment
    })
    newReview.value = { rating: '', comment: '' }
  } finally {
    submittingReview.value = false
  }
}

// Начать редактирование
function startEdit(r) {
  editId.value     = r.id
  editReview.value = { rating: r.rating, comment: r.comment }
}

// Отменить редактирование
function cancelEdit() {
  editId.value     = null
  editReview.value = { rating: '', comment: '' }
}

// Сохранить правки
async function updateReview() {
  submittingReview.value = true
  try {
    await reviewsStore.updateReview({
      reviewId:   editId.value,
      product_id: product.value.id,
      rating:     editReview.value.rating,
      comment:    editReview.value.comment
    })
    cancelEdit()
  } finally {
    submittingReview.value = false
  }
}

// Удалить отзыв
async function deleteReview(id) {
  if (!confirm('Вы уверены?')) return
  submittingReview.value = true
  try {
    await reviewsStore.deleteReview({
      reviewId:   id,
      product_id: product.value.id
    })
  } finally {
    submittingReview.value = false
  }
}

async function addToCart() {
  successMessage.value = null
  try {
    await cartStore.addToCart({
      product_id: product.value.id,
      quantity: 1,
      size: selectedSize.value
    })
    successMessage.value = `Добавлен размер ${selectedSize.value}`
  } catch {
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
  }
}

// Lightbox methods
function openLightbox() { lightboxOpen.value = true }
function closeLightbox() { lightboxOpen.value = false }
function prevImage() {
  currentIndex.value = (currentIndex.value + images.value.length - 1) % images.value.length
  selectedImage.value = images.value[currentIndex.value]
}
function nextImage() {
  currentIndex.value = (currentIndex.value + 1) % images.value.length
  selectedImage.value = images.value[currentIndex.value]
}
function goToImage(idx) {
  currentIndex.value = idx
  selectedImage.value = images.value[idx]
}

function onImgError(e) { e.target.src = placeholder }
function formatPrice(val) { return Number(val).toLocaleString('ru-RU') }

const formattedDescription = computed(() => product.value.description || '')

onMounted(loadProduct)
</script>

<style scoped>
.product-detail {
  display: flex;
  flex-wrap: wrap;
  padding: 2rem;
  background-color: #1a1a1a;
  color: #fff;
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
}
.loader,
.error-message,
.success-message {
  width: 100%;
  text-align: center;
  font-size: 1.2rem;
  margin-top: 2rem;
}
.error-message { color: #f66; }
.success-message { color: #6f6; }

.image-section {
  flex: 1 1 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
  position: relative;
}

.main-image {
  width: 100%;
  max-width: 500px;
  overflow: visible;
}

.product-image {
  width: 100%;
  height: auto;
  border-radius: 1rem;
  object-fit: contain;
  transition: transform 0.3s ease;
  cursor: zoom-in;
}
.thumbnails {
  overflow-x: auto;
  scrollbar-width: none;      /* Firefox */
  -ms-overflow-style: none;   /* IE/Edge */
}
.thumbnails {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}
.thumbnails::-webkit-scrollbar {
  display: none;              /* Chrome, Safari */
}
.thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 0.5rem;
  cursor: pointer;
  opacity: 0.8;
  border: 2px solid transparent;
  transition: opacity 0.2s, transform 0.2s, border-color 0.2s;
}
.thumb:hover { opacity: 1; transform: scale(1.1); }
.thumb.active { opacity: 1; border-color: #000;; }

.info-section {
  flex: 1 1 300px;
  padding: 1rem 2rem;
}
.title { font-size: 2rem; margin-bottom: 1rem; color: var(--accent-color); }
.price { font-size: 1.5rem; color: #ffffff; margin-bottom: 1rem; }
.description { font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem; }

.size-selector {
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.size-selector label { font-size: 1rem; }
.size-selector select {
  background: #2a2a2a;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem;
  min-width: 100px;
}

.add-to-cart {
  margin-top: 1rem;
  background: #ffffff;
  border: none;
  color: #1a1a1a;
  font-size: 1.1rem;
  padding: 0.6rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
}
.add-to-cart:disabled { opacity: 0.6; cursor: default; }
.add-to-cart:hover:not(:disabled) { background: #ffffff; }

.recommendations-section {
  width: 100%;
  margin-top: 3rem;
}
.recommendations-section h3 {
  width: 100%;
  text-align: center;
  color: #fff;
  margin-bottom: 1rem;
}
.recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

/* Lightbox Styles */
.lightbox {
  position: fixed; top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.9);
  display: flex; align-items: center; justify-content: center;
  flex-direction: column;
  z-index: 2000;
}
.lightbox-image {
  max-width: 60vw; max-height: 60vh;
}
.lightbox .nav {
  position:absolute; top:50%; font-size:2rem;
  background:none; border:none; color:#fff;
  cursor:pointer; padding:1rem;
}
.lightbox .prev { left:2%; }
.lightbox .next { right:2%; }
.lightbox .close-btn {
  position:absolute; top:1rem; right:1rem;
  font-size:1.5rem; background:none; border:none;
  color:#fff; cursor:pointer;
}
.lightbox-thumbs {
  display:flex; gap:0.5rem; margin-top:1rem; overflow-x:auto;
}
.lightbox-thumbs img {
  width:60px; height:60px; object-fit:cover;
  border:2px solid transparent; cursor:pointer;
}
.lightbox-thumbs img.active { border-color:#fff; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeIn 0.4s ease-in-out; }
.new-review-form,
.edit-form {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #222;
  border-radius: 4px;
}
.form-group {
  margin-bottom: 0.5rem;
}
.form-group label {
  display: block;
  color: #ccc;
  margin-bottom: 0.25rem;
}
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.4rem;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 4px;
}
button {
  margin-right: 0.5rem;
}
.btn-delete {
  color: #f66;
}
.btn-cancel {
  background: transparent;
  color: #ccc;
}
/* Секция отзывов */
.reviews-section {
  width: 100%;
  margin: 2rem 0;
}
.reviews-section h3 {
  color: #fff;
  margin-bottom: 0.5rem;
}
.loader-small {
  text-align: center;
  color: #ccc;
  margin: 1rem 0;
}
.reviews-container {
  max-height: 300px;
  overflow-y: auto;
  padding: 1rem;
  border: 2px solid rgb(255, 255, 255);
  border-radius: 8px;
  background: #111;
}
.no-reviews {
  color: #aaa;
  text-align: center;
  margin-bottom: 1rem;
}
.new-review-form,
.edit-form {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #222;
  border-radius: 4px;
}
.form-group {
  margin-bottom: 0.5rem;
}
.form-group label {
  display: block;
  color: #ccc;
  margin-bottom: 0.25rem;
}
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.4rem;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 4px;
}
.review-card {
  padding: 0.5rem;
  border-bottom: 1px solid #333;
  color: #eee;
}
.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}
.review-user {
  font-weight: bold;
}
.review-rating {
  font-size: 1rem;
  color: rgb(255, 255, 255);
}
.review-comment {
  margin: 0.5rem 0;
}
.review-date {
  color: #888;
  font-size: 0.75rem;
}
.review-actions {
  margin-top: 0.5rem;
}
.review-actions button {
  margin-right: 0.5rem;
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
}
.review-actions .btn-delete {
  color: #f66;
}
.review-actions .btn-cancel {
  color: #aaa;
}
.btn-submit-review {
  background: #ccc;
  color: #1a1a1a;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.btn-submit-review:hover:not(:disabled) {
  background: #ffffff;
}
.recommend-link {
  display: block;
  text-decoration: none;
}
</style>
