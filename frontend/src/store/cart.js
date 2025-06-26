import { defineStore } from 'pinia'
import api from '@/api'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),

  actions: {
    // Загрузить корзину
    async fetchCart() {
      this.loading = true
      this.error   = null
      try {
        const res = await api.get('/cart')
        this.items = res.data.items.map(i => ({
          id:        i.id,
          productId: i.product.id,
          name:      i.product.name,
          price:     parseFloat(i.product.price),
          image:     i.product.image,
          quantity:  i.quantity,
          size:      i.size,
          lineTotal: parseFloat(i.product.price) * i.quantity
        }))
      } catch (err) {
        console.error('Ошибка загрузки корзины', err)
        this.error = err.response?.data?.error || err.message
      } finally {
        this.loading = false
      }
    },

    // Добавить позицию
    async addToCart({ product_id, quantity = 1, size }) {
      this.loading = true
      this.error   = null
      try {
        await api.post('/cart', { product_id, quantity, size })
        await this.fetchCart()
      } catch (err) {
        console.error('Ошибка добавления в корзину', err)
        this.error = err.response?.data?.error || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    // Обновить позицию (PUT /cart)
    async updateItem({ product_id, quantity, size }) {
      this.loading = true
      this.error   = null
      try {
        await api.put('/cart', { product_id, quantity, size })
        await this.fetchCart()
      } catch (err) {
        console.error('Ошибка обновления элемента корзины', err)
        this.error = err.response?.data?.error || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    // Удалить одну позицию (DELETE /cart/:product_id)
    async removeItem(product_id) {
      this.loading = true
      this.error   = null
      try {
        await api.delete(`/cart/${product_id}`)
        await this.fetchCart()
      } catch (err) {
        console.error('Ошибка удаления элемента корзины', err)
        this.error = err.response?.data?.error || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    // Очистить корзину
    async clearCart() {
      this.loading = true
      this.error   = null
      try {
        await api.delete('/cart/clear')
        this.items = []
      } catch (err) {
        console.error('Ошибка очистки корзины', err)
        this.error = err.response?.data?.error || err.message
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
