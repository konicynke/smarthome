import { clearToken, getToken, setToken } from "./auth.js";
import router from "./router.js";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const headers = { ...options.headers };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, {
    ...options,
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (response.status === 401 && token) {
    clearToken();
    router.push({ name: "login", query: { redirect: router.currentRoute.value.fullPath } });
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = (await response.json()).detail ?? detail;
    } catch {
      // body is not JSON
    }
    throw new ApiError(response.status, detail);
  }
  return response.json();
}

export async function login(username, password) {
  const data = await request("/api/login", {
    method: "POST",
    body: { username, password },
  });
  setToken(data.access_token);
}

export function fetchDevices() {
  return request("/api/devices");
}
