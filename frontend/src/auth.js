import { computed, ref } from "vue";

const STORAGE_KEY = "smarthome.token";

function readStoredToken() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function decodePayload(token) {
  try {
    const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(part));
  } catch {
    return null;
  }
}

function isExpired(token) {
  const payload = decodePayload(token);
  return !payload || (payload.exp && payload.exp * 1000 <= Date.now());
}

const stored = readStoredToken();
const token = ref(stored && !isExpired(stored) ? stored : null);

export const username = computed(() => (token.value ? decodePayload(token.value)?.sub : null));

export function getToken() {
  if (token.value && isExpired(token.value)) {
    clearToken();
  }
  return token.value;
}

export function isLoggedIn() {
  return Boolean(getToken());
}

export function setToken(value) {
  token.value = value;
  try {
    localStorage.setItem(STORAGE_KEY, value);
  } catch {
    // storage unavailable, keep the token in memory only
  }
}

export function clearToken() {
  token.value = null;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // nothing stored
  }
}
