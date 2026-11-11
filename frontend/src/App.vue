<script setup>
import { useRouter } from "vue-router";

import { clearToken, username } from "./auth.js";

const router = useRouter();

function logout() {
  clearToken();
  router.push({ name: "login" });
}
</script>

<template>
  <header class="topbar">
    <span class="brand">Smart Home</span>
    <div v-if="username" class="user">
      <span>{{ username }}</span>
      <button class="link-button" type="button" @click="logout">Wyloguj</button>
    </div>
  </header>
  <main class="content">
    <RouterView />
  </main>
</template>
