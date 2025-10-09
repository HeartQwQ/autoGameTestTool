import { createMemoryHistory, createRouter } from 'vue-router'

import { navData } from "@/router/navbar"
import { getAllUrls } from "@/utils/index"

const allUrls = getAllUrls(navData.navMain)
allUrls.push({ path: '/', redirect: '/auto/video' })
console.log('所有路由:', allUrls)

const routes = allUrls

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router