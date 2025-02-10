<template>
  <div class="sidebar-container" :class="{hideSidebar: collapse}">
    <div class="logo">
      <img src="@/assets/images/logo.png" />
      <transition name="sidebarLogoFade">
        <div class="title" v-show="!collapse">薄冰后台</div>
      </transition>
    </div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :router="true"
        :default-active="activeIndex"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :collapse="collapse"
        :active-text-color="variables.menuActiveText"
        :collapse-transition="false"
        mode="vertical"
      >
        <template v-for="(menu, firstIndex) in authMenu">
          <el-submenu
            :key="firstIndex"
            :index="menu.path || menu.meta.title"
            v-if="menu.meta.sub">
            <template slot="title">
              <svg class="icon" aria-hidden="true">
                <use :xlink:href="`#${menu.meta.icon}`"></use>
              </svg>
              <span>{{ menu.meta.title }}</span>
            </template>
            <el-menu-item
              v-for="(secondMenu, secondIndex) in menu.children"
              :key="secondIndex"
              class="sub-item"
              :index="`${menu.path}/${secondMenu.path}`">
              {{secondMenu.meta.title }}
            </el-menu-item>
          </el-submenu>
          <el-menu-item
            :key="firstIndex"
            :index="menu.path || menu.meta.title"
            v-else-if="menu.path && !menu.meta.sub">
             <svg class="icon" aria-hidden="true">
                <use :xlink:href="`#${menu.meta.icon}`"></use>
              </svg>
            <span slot="title">{{ menu.meta.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import variables from '@/style/variables.scss'
import router, { generateRoute } from '@/router/index'

export default {
  data () {
    return {
    }
  },
  computed: {
    ...mapState({
      collapse: 'collapse',
      routes: state => state.auth.routes,
    }),
    variables() {
      return variables
    },
    activeIndex () {
      return this.$route.path
    },
    authMenu () {
      return router
    },
  }
}
</script>
