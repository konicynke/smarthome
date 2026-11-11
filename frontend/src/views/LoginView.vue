<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { ApiError, login } from "../api.js";

const route = useRoute();
const router = useRouter();

const username = ref("");
const password = ref("");
const error = ref("");
const busy = ref(false);

async function submit() {
  error.value = "";
  busy.value = true;
  try {
    await login(username.value.trim(), password.value);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    router.replace(redirect.startsWith("/") ? redirect : "/");
  } catch (e) {
    error.value =
      e instanceof ApiError && e.status === 401
        ? "Nieprawidłowy login lub hasło."
        : "Nie udało się połączyć z serwerem.";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <form class="login card" @submit.prevent="submit">
    <h1>Logowanie</h1>
    <label>
      Login
      <input v-model="username" autocomplete="username" required autofocus />
    </label>
    <label>
      Hasło
      <input v-model="password" type="password" autocomplete="current-password" required />
    </label>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <button class="primary" type="submit" :disabled="busy">
      {{ busy ? "Logowanie…" : "Zaloguj" }}
    </button>
  </form>
</template>
