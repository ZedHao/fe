<template>
  <header class="header">
    <div class="logo">
      <img src="../assets/logo.png" alt="Logo" class="logo-img" />
      <span class="site-name">大绿黄财经科技</span>
    </div>
    <nav class="nav">
      <ul class="nav-list">
        <li class="nav-item"><a href="#" class="nav-link">黄金</a></li>
        <li class="nav-item"><a href="#" class="nav-link">基金</a></li>
        <li class="nav-item"><a href="#" class="nav-link">股票</a></li>
        <li class="nav-item"><a href="#" class="nav-link">可转债</a></li>
        <li class="nav-item"><a href="#" class="nav-link">关于我们</a></li>
      </ul>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'Header',
};
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #0d0d0d;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
}

.logo-img {
  height: 40px;
  margin-right: 10px;
}

.site-name {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #00ffcc, #cc00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 1.5rem;
}

.nav-link {
  color: #ccc;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #00ffcc;
  text-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc;
}
</style>
