import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from '@auth0/auth0-vue'

import Landing from '../views/Landing.vue'
import Tool from '../views/Tool.vue'
import Callback from '../views/Callback.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Landing', component: Landing },
    { path: '/tool', name: 'Tool', component: Tool, beforeEnter: authGuard },
    { path: '/callback', name: 'Callback', component: Callback },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
