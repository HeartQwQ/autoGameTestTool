import {
  AudioWaveform,
  Command,
  GalleryVerticalEnd,
  SquareTerminal,
} from "lucide-vue-next"
import type { LucideIcon } from "lucide-vue-next"
import { Component } from 'vue'

interface User {
  name: string
  email: string
  avatar: string
}

interface Team {
  name: string
  logo: Component
  plan: string
}

export interface NavItem {
  title: string
  url: string | object
  icon?: LucideIcon
  isActive?: boolean
  items?: {
    title: string
    url: string | object
  }[]
}

interface NavData {
  collapsible: "offcanvas" | "icon" | "none",
  user: User
  teams: Team[]
  navMain: NavItem[]
}

import Video from '@/pages/auto/Video.vue'
import Auto2 from '@/pages/auto/auto2.vue'

export const navData: NavData = {
  collapsible: "icon",
  user: {
    name: "v_yuxilong(龙昱樨)",
    email: "v_yuxilong@tencent.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "CJ GAME",
      logo: GalleryVerticalEnd,
      plan: "Game For Peace",
    },
    {
      name: "和平UE5升级",
      logo: AudioWaveform,
      plan: "Peace Up UE5",
    },
    {
      name: "和平精英_潘多拉营销活动",
      logo: Command,
      plan: "Game Pandora",
    },
  ],
  navMain: [
    {
      title: "自动化",
      url: { path: '/auto', redirect: '/auto/video' },
      icon: SquareTerminal,
      isActive: true,
      items: [
        {
          title: "视频找图",
          url: { path: '/auto/video', component: Video },
        },
        {
          title: "自动化2",
          url: { path: '/auto/auto2', component: Auto2 },
        }
      ],
    }
  ]
}