<template>
  <div class="home">
    <Header />
    <main class="main-content">
      <h1 class="welcome-text">欢迎来到财经科技</h1>
      <p class="sub-text">探索最新的财经资讯，掌握投资先机。</p>
    </main>
  </div>
</template>

<script>
import Header from '@/components/Header.vue';

export default {
  name: 'Home',
  components: {
    Header,
  },
};
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: radial-gradient(circle, #0d0d0d, #000);
  color: #fff;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.welcome-text {
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #00ffcc, #cc00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: glow 2s infinite alternate;
}

.sub-text {
  font-size: 1.5rem;
  color: #ccc;
}

@keyframes glow {
  0% {
    text-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc, 0 0 20px #00ffcc;
  }
  100% {
    text-shadow: 0 0 10px #cc00ff, 0 0 20px #cc00ff, 0 0 30px #cc00ff;
  }
}
</style>
