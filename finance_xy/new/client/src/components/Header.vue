<template>
  <header class="header">
    <div class="header-left">
      <img src="/logo.jpg" alt="猪猪" class="logo" />
      <span class="brand">狗狗基金</span>
    </div>
    <nav class="nav">
      <router-link to="/">折溢价</router-link>
      <router-link to="/blacklist">黑名单</router-link>
      <router-link to="/calendar">日历</router-link>
      <router-link to="/futures">期货</router-link>
      <router-link to="/house">房价</router-link>
      <router-link to="/perks">股东福利</router-link>
    </nav>
  </header>
</template>

<script setup lang="ts">
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #0f1219;
  border-bottom: 1px solid #262e3f;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.logo { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.brand {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(45deg, #4f7eff, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.nav { display: flex; gap: 16px; flex-wrap: wrap; }
.nav a {
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
}
.nav a.router-link-active { color: #4f7eff; }
.nav a:hover { color: #e2e8f0; }
</style>
