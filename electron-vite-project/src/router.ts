import { createMemoryHistory, createRouter } from 'vue-router'

import Video from './pages/Video.vue'

const routes = [
    { path: '/', component: Video },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router