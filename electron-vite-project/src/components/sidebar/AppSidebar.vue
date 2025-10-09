<script setup lang="ts">
import { navData as data } from "@/router/navbar"
import NavMain from "./NavMain.vue"
// import NavProjects from "./NavProjects.vue"
import NavUser from "./NavUser.vue"
import TeamSwitcher from "./TeamSwitchar.vue"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
</script>

<template>
  <Sidebar :collapsible="data.collapsible">
    <!-- 侧边栏顶部 -->
    <SidebarHeader>
      <TeamSwitcher :teams="data.teams" />
    </SidebarHeader>
    <!-- 侧边栏主体 -->
    <SidebarContent>
      <NavMain :items="data.navMain" />
      <!-- <NavProjects :projects="data.projects" /> -->
    </SidebarContent>
    <!-- 侧边栏底部 -->
    <SidebarFooter>
      <NavUser :user="data.user" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
