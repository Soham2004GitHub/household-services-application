
<script setup>
//import Navbar from './components/navbar.js'
//import router from './utils/router.js'
//import { RouterView } from 'vue-router'

import Navbar from ".src/components/navbar.js"
import router from ".src/utils/router.js"
import store from ".src/utils/store.js"
</script>

<template>
  <div>
    <Navbar />
    <router-view />
  </div>
</template>
