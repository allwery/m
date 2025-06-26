<template>
  <div class="reviews-container animate-fade-in">
    <Header />
    <div class="reviews-content">
      <h1 class="title">Отзывы о товаре</h1>

      <div class="form-group">
        <label for="rating">Оценка:</label>
        <select v-model.number="newReview.rating" id="rating">
          <option disabled value="">-- выберите --</option>
          <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

      <textarea
        v-model="newReview.comment"
        placeholder="Оставьте ваш отзыв..."
      ></textarea>

      <button @click="submitReview" :disabled="reviewsStore.loading || submitting">
        {{ submitting ? 'Отправка...' : 'Отправить отзыв' }}
      </button>

      <p v-if="reviewsStore.error" class="error-message">{{ reviewsStore.error }}</p>

      <div v-if="!reviewsStore.loading && reviewsStore.list.length" class="review-list">
        <div v-for="r in reviewsStore.list" :key="r.id" class="review-item">
          <div class="review-header">
            <span class="rating">Оценка: {{ r.rating }}/5</span>
            <span class="date">{{ formatDate(r.created_at) }}</span>
          </div>
          <p class="comment">{{ r.comment }}</p>
        </div>
      </div>

      <div v-else-if="!reviewsStore.loading && !reviewsStore.list.length" class="no-reviews">
        Нет отзывов
      </div>

      <div v-if="reviewsStore.loading" class="loader">Загрузка отзывов...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useReviewsStore } from '@/store/reviews'
import Header from '@/components/header.vue'

const route = useRoute()
const reviewsStore = useReviewsStore()
const submitting = ref(false)

const newReview = ref({ rating: '', comment: '' })

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function fetchReviews() {
  await reviewsStore.fetchReviews(route.params.productId)
}

async function submitReview() {
  if (!newReview.value.rating || !newReview.value.comment.trim()) {
    reviewsStore.error = 'Пожалуйста, укажите рейтинг и комментарий'
    return
  }
  submitting.value = true
  try {
    await reviewsStore.postReview({
      product_id: route.params.productId,
      rating: newReview.value.rating,
      comment: newReview.value.comment.trim()
    })
    newReview.value = { rating: '', comment: '' }
  } finally {
    submitting.value = false
  }
}

onMounted(fetchReviews)
</script>

<style scoped>
.reviews-container {
  background: #111;
  color: #fff;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-top: 5rem;
}
.reviews-content {
  width: 90%;
  max-width: 600px;
  margin: 0 auto;
  background: #222;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 0 10px rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 0.5rem;
}
.form-group select,
textarea {
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  background: #333;
  color: #fff;
}
textarea {
  resize: vertical;
  min-height: 100px;
}
button {
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  background: #444;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}
button:disabled {
  opacity: 0.6;
  cursor: default;
}
button:hover:not(:disabled) {
  background: #666;
}
.review-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}
.review-item {
  background: #333;
  padding: 1rem;
  border-radius: 0.5rem;
}
.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #ccc;
}
.comment {
  font-size: 1rem;
  color: #eee;
}
.error-message {
  color: #f66;
  text-align: center;
  font-size: 0.9rem;
}
.no-reviews,
.loader {
  text-align: center;
  color: #aaa;
  font-size: 1.1rem;
  margin-top: 1rem;
}
.animate-fade-in {
  animation: fadeIn 0.8s ease forwards;
  opacity: 0;
}
@keyframes fadeIn { to { opacity: 1; } }
</style>
