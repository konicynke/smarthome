import { createRouter, createWebHistory } from "vue-router";

import { isLoggedIn } from "./auth.js";
import DashboardView from "./views/DashboardView.vue";
import LoginView from "./views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: DashboardView, meta: { requiresAuth: true } },
    { path: "/login", name: "login", component: LoginView },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && isLoggedIn()) {
    return { name: "dashboard" };
  }
});

export default router;
