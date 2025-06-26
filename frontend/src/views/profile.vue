<template>
  <div class="profile-container animate-fade-in">
    <div class="profile-content">
      <h1 class="title">Мой аккаунт</h1>

      <!-- Навигация по разделам -->
      <nav class="profile-nav">
        <button :class="{ active: tab==='orders' }" @click="selectTab('orders')">Заказы</button>
        <button :class="{ active: tab==='addresses' }" @click="selectTab('addresses')">Адреса</button>
        <button :class="{ active: tab==='profile' }" @click="selectTab('profile')">Профиль</button>
        <button class="logout-btn" @click="authStore.logout()">Выйти</button>
      </nav>

      <!-- === Заказы === -->
      <div v-if="tab==='orders'" class="section">
        <div v-if="loadingOrders" class="loader">Загрузка заказов...</div>
        <div v-else>
          <template v-if="orders.length">
            <table class="orders-table">
              <thead>
                <tr>
                  <th>№</th><th>Дата</th><th>Статус</th><th>Итого</th><th>Трек номер</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in orders" :key="o.id">
                  <td class="order-number">№{{ o.id }}</td>
                  <td>{{ formatDate(o.created_at) }}</td>
                  <td>{{ o.status }}</td>
                  <td>{{ formatPrice(o.total_amount) }}</td>
                  <td>
                    <RouterLink :to="{ name:'OrderDetails', params:{ orderId:o.id } }">
                      <button class="btn-small">Просмотр</button>
                    </RouterLink>
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
          <template v-else>
            <div class="no-items">
              <p>Вы ещё не сделали ни одного заказа.</p>
              <RouterLink to="/catalog">
                <button class="btn-small">Сделать заказ</button>
              </RouterLink>
            </div>
          </template>
        </div>
      </div>

      <!-- === Адреса === -->
      <div v-else-if="tab==='addresses'" class="section">
        <div v-if="loadingAddresses" class="loader">Загрузка адресов...</div>
        <div v-else>
          <template v-if="addresses.length">
            <ul class="addresses-list">
              <li v-for="addr in addresses" :key="addr.id">
                <template v-if="editedAddressId !== addr.id">
                  <p>{{ addr.street }}, {{ addr.city }}, {{ addr.postal_code }}, {{ addr.country }}</p>
                  <button class="btn-small" @click="startEdit(addr)">Изменить</button>
                  <button class="btn-small" @click="deleteAddress(addr.id)">Удалить</button>
                </template>
                <template v-else>
                  <input v-model="editedAddr.street" placeholder="Улица, дом" />
                  <input v-model="editedAddr.city" placeholder="Город" />
                  <input v-model="editedAddr.postal_code" placeholder="Индекс" />
                  <input v-model="editedAddr.country" placeholder="Страна" />
                  <button
                    class="btn-small"
                    :disabled="!canSaveEdited"
                    @click="saveEdit(addr.id)"
                  >
                    Сохранить
                  </button>
                  <button class="btn-small" @click="cancelEdit">Отмена</button>
                </template>
              </li>
            </ul>
          </template>
          <template v-else>
            <div class="no-items">
              <p>У вас пока нет сохранённых адресов.</p>
            </div>
          </template>

          <div class="address-form">
            <h3>Добавить новый адрес</h3>
            <input v-model="newAddr.street" placeholder="Улица, дом" />
            <input v-model="newAddr.city" placeholder="Город" />
            <input v-model="newAddr.postal_code" placeholder="Индекс" />
            <input v-model="newAddr.country" placeholder="Страна" />
            <button class="btn-small" :disabled="!canSaveNew" @click="saveNew">
              Сохранить адрес
            </button>
          </div>
        </div>
      </div>

      <!-- === Профиль === -->
      <div v-else class="section">
        <div class="info-block">
          <p><strong>Email:</strong> {{ authStore.user.email }}</p>
          <p class="inline-input">
            <strong>Имя (оно нужно для отзывов):</strong>
            <input v-model="username" placeholder="Укажите имя" />
          </p>
          <p>
             <strong>Реферальный код: </strong>
             <code>{{ authStore.user.referral_code }}</code>
          </p>
        </div>
        <button
          class="btn-small"
          :disabled="!username.trim()"
          @click="saveUsername"
        >
          Сохранить имя
        </button>

        <hr />

        <form class="password-form" @submit.prevent="changePassword">
          <h3>Сменить пароль</h3>
          <input v-model="pw.current" type="password" placeholder="Текущий пароль" />
          <input v-model="pw.new" type="password" placeholder="Новый пароль" minlength="8" />
          <input v-model="pw.confirm" type="password" placeholder="Повторите новый пароль" minlength="8" />
          <button type="submit" class="btn-small":disabled="!canChangePassword">Обновить пароль</button>
        </form>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const authStore        = useAuthStore()
const route            = useRoute()
const router           = useRouter()

// Выбираем вкладку из query или по-умолчанию «orders»
const tab = ref(route.query.tab || 'orders')

// — — Заказы — —
const orders         = ref([])
const loadingOrders  = ref(false)

async function fetchOrders() {
  loadingOrders.value = true
  try {
    const res = await api.get('/orders')  // GET /orders возвращает список текущего пользователя
    orders.value = res.data
  } catch (e) {
    console.error('Не удалось загрузить заказы', e)
  } finally {
    loadingOrders.value = false
  }
}

// — — Адреса — —
const addresses           = ref([])
const loadingAddresses    = ref(false)
const newAddr             = reactive({ street:'', city:'', postal_code:'', country:'' })
const editedAddressId     = ref(null)
const editedAddr          = reactive({ street:'', city:'', postal_code:'', country:'' })

const canSaveNew = computed(() =>
  newAddr.street && newAddr.city && newAddr.postal_code && newAddr.country
)
const canSaveEdited = computed(() =>
  editedAddr.street && editedAddr.city && editedAddr.postal_code && editedAddr.country
)

async function fetchAddresses() {
  loadingAddresses.value = true
  try {
    const res = await api.get('/user/addresses')
    addresses.value = res.data
  } catch (e) {
    console.error('Не удалось загрузить адреса', e)
  } finally {
    loadingAddresses.value = false
  }
}

// CRUD адресов
function selectTab(name) {
  tab.value = name
  router.replace({ query: { ...route.query, tab: name } })
}

function startEdit(addr) {
  editedAddressId.value = addr.id
  Object.assign(editedAddr, addr)
}

function cancelEdit() {
  editedAddressId.value = null
  Object.assign(editedAddr, { street:'', city:'', postal_code:'', country:'' })
}

async function saveNew() {
  try {
    await api.post('/user/addresses', {
      street:      newAddr.street.trim(),
      city:        newAddr.city.trim(),
      postal_code: newAddr.postal_code.trim(),
      country:     newAddr.country.trim()
    })
    Object.assign(newAddr, { street:'', city:'', postal_code:'', country:'' })
    selectTab('addresses')
    await fetchAddresses()
  } catch (err) {
    alert(err.response?.data?.errors?.join(', ') || 'Ошибка при добавлении адреса')
  }
}

async function saveEdit(id) {
  try {
    await api.put(`/user/addresses/${id}`, { ...editedAddr })
    cancelEdit()
    await fetchAddresses()
  } catch (err) {
    alert(err.response?.data?.errors?.join(', ') || 'Ошибка при сохранении адреса')
  }
}

async function deleteAddress(id) {
  try {
    await api.delete(`/user/addresses/${id}`)
    await fetchAddresses()
  } catch {
    alert('Ошибка при удалении адреса')
  }
}

// — — Профиль — —
const username = ref(authStore.user?.username || '')

async function saveUsername() {
  const name = username.value.trim()
  if (!name) return
  try {
    await api.put('/user/profile', { username: name })
    authStore.user.username = name
    localStorage.setItem('user', JSON.stringify(authStore.user))
    alert('Имя сохранено')
  } catch (err) {
    alert(err.response?.data?.errors?.join(', ') || 'Ошибка при сохранении имени')
  }
}

// Смена пароля
const pw = reactive({ current:'', new:'', confirm:'' })
const canChangePassword = computed(() =>
  pw.current && pw.new.length >= 8 && pw.new === pw.confirm
)

async function changePassword() {
  try {
    await api.put('/user/password', {
      current_password: pw.current,
      new_password:     pw.new
    })
    pw.current = pw.new = pw.confirm = ''
    alert('Пароль обновлён')
  } catch (err) {
    alert(err.response?.data?.error || 'Ошибка при смене пароля')
  }
}

// Утилиты
function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}
function formatPrice(x) {
  return Number(x).toLocaleString('ru-RU') + ' ₽'
}

// При монтировании — подтягиваем профиль, заказы и адреса
onMounted(async () => {
  await authStore.fetchUserProfile()
  await fetchOrders()
  await fetchAddresses()
})
</script>


<style scoped>
/* Сохранил прежнюю палитру, шрифты и отступы */
.profile-container { background:#111; color:#fff; min-height:100vh; padding-top:5rem; display:flex; justify-content:center; }
.profile-content { background:#222; padding:2rem; border-radius:1rem; width:800px; box-shadow:0 0 10px rgba(255,255,255,0.05); font-family:'Inter',sans-serif; }

/* Навигация */
.profile-nav { display:flex; gap:1rem; margin-bottom:1.5rem; }
.profile-nav button { background:none; border:none; color:#aaa; padding:.5rem 1rem; cursor:pointer; }
.profile-nav button.active { color:#fff; border-bottom:2px solid #fff; }
.logout-btn { margin-left:auto; color:#f66; }

/* Общие */
.section { margin-top:1rem; }
.loader { color:#aaa; text-align:center; padding:1rem 0; }

/* Заказы */
.orders-table { width:100%; border-collapse:collapse; }
.orders-table th, .orders-table td { padding:.75rem; border-bottom:1px solid #333; }
.no-items { text-align:center; color:#aaa; padding:2rem 0; }

/* Адреса */
.addresses-list { list-style:none; padding:0; margin:0 0 1rem; }
.addresses-list li { display:flex; align-items:center; gap:.5rem; padding:.75rem; background:#333; border-radius:.5rem; margin-bottom:.5rem; }
.address-form { background:#111; padding:1rem; border-radius:.5rem; }
.address-form input { width:auto; background:#111; border:1px solid #333; border-radius:.5rem; padding:.5rem; color:#fff; margin-right:.75rem; }

/* Профиль */
.info-block { background:#333; padding:1rem; border-radius:.5rem; }
.inline-input { display:flex; align-items:center; gap:.5rem; margin-top:.5rem; }
.inline-input input { background:#111; border:1px solid #333; border-radius:.5rem; padding:.5rem; color:#fff; }

/* Смена пароля */
.password-form { background:#111; padding:1rem; border-radius:.5rem; margin-top:1rem; }
.password-form input { width:100%; background:#111; border:1px solid #333; border-radius:.5rem; padding:.5rem; color:#fff; margin-bottom:.5rem; }

/* Кнопки */
.btn-small {
  background: #fff;
  border: none;
  color: #000;
  padding: .5rem 1rem;
  border-radius: .5rem;
  cursor: pointer;
}
.btn-small:disabled {
  background: #888 !important;
  color: #000 !important;
  opacity: 1;
  cursor: default;
}

/* Анимация */
.animate-fade-in { animation:fadeIn .6s ease forwards; opacity:0; }
@keyframes fadeIn { to { opacity:1; } }
</style>
