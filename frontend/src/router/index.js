import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Views
import Home            from '@/views/home.vue'
import Catalog         from '@/views/catalog.vue'
import ProductDetail   from '@/views/productDetail.vue'
import Cart            from '@/views/cart.vue'
import Checkout        from '@/views/checkout.vue'
import Reviews         from '@/views/reviews.vue'
import Login           from '@/views/login.vue'
import Register        from '@/views/register.vue'
import Profile         from '@/views/profile.vue'
import Admin           from '@/views/admin.vue'
import Contacts        from '@/views/Contacts.vue'
import UserAgreement   from '@/views/UserAgreement.vue'
import PrivacyPolicy   from '@/views/PrivacyPolicy.vue'

const routes = [
  { path: '/',               name: 'Home',            component: Home },
  { path: '/catalog',        name: 'Catalog',         component: Catalog },
  {
    path: '/product/:productId',
    name: 'productDetail',
    component: ProductDetail,
    props: true
  },
  {
    path: '/cart',
    name: 'Cart',
    component: Cart,
    meta: { requiresAuth: true } // Доступно только авторизованным
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: Checkout,
    meta: { requiresAuth: true }
  },
  {
    path: '/reviews/:productId?',
    name: 'Reviews',
    component: Reviews,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { hideFooter: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { hideFooter: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAdmin: true }
  },
  { path: '/contacts',      name: 'Contacts',      component: Contacts },
  { path: '/user-agreement',name: 'UserAgreement', component: UserAgreement },
  { path: '/privacy-policy',name: 'PrivacyPolicy', component: PrivacyPolicy },
  // Redirect неизвестных путей на главную
  { path: '/:catchAll(.*)', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Глобальный guard для авторизации
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const isAuth = !!auth.accessToken
  const isAdmin = auth.user?.is_admin

  if (to.meta.requiresAuth && !isAuth) {
    // если не залогинен — перенаправляем на логин и запоминаем куда вернуться
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  if (to.meta.requiresAdmin && !isAdmin) {
    return next({ name: 'Home' })
  }
  next()
})

export default router