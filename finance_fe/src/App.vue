<template>
  <div id="app">
    <Header />
    <router-view></router-view>
  </div>
</template>

<script>
import Home from './views/Home.vue';

export default {
  name: 'App',
  components: {
    Home,
  },
};
</script>

<style>
body {
  margin: 0;
  font-family: 'Arial', sans-serif;
  background-color: #000;
  color: #fff;
}
</style>
