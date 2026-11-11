import { onBeforeUnmount, ref } from "vue";

import { getToken } from "./auth.js";

const MAX_RETRY_DELAY = 30000;

export function useLiveReadings(onDevice) {
  const connected = ref(false);
  let socket = null;
  let retryDelay = 1000;
  let retryTimer = null;
  let stopped = false;

  function connect() {
    const token = getToken();
    if (stopped || !token) {
      return;
    }
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${location.host}/ws?token=${encodeURIComponent(token)}`);

    socket.onopen = () => {
      connected.value = true;
      retryDelay = 1000;
    };
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "reading") {
        onDevice(message.device);
      }
    };
    socket.onclose = () => {
      connected.value = false;
      socket = null;
      if (!stopped) {
        retryTimer = setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY);
      }
    };
  }

  connect();

  onBeforeUnmount(() => {
    stopped = true;
    clearTimeout(retryTimer);
    socket?.close();
  });

  return { connected };
}
