<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { fetchDevices } from "../api.js";
import RoomCard from "../components/RoomCard.vue";
import { useLiveReadings } from "../live.js";

const REFRESH_INTERVAL = 30000;

const devices = ref(new Map());
const loading = ref(true);
const error = ref("");
let refreshTimer = null;

const rooms = computed(() => {
  const grouped = new Map();
  for (const device of devices.value.values()) {
    if (!grouped.has(device.room)) {
      grouped.set(device.room, []);
    }
    grouped.get(device.room).push(device);
  }
  return [...grouped.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([room, list]) => ({
      room,
      devices: list.sort((a, b) => a.device_id.localeCompare(b.device_id)),
    }));
});

async function refresh() {
  try {
    const list = await fetchDevices();
    devices.value = new Map(list.map((device) => [device.device_id, device]));
    error.value = "";
  } catch {
    error.value = "Nie udało się pobrać listy urządzeń.";
  } finally {
    loading.value = false;
  }
}

function updateDevice(device) {
  const next = new Map(devices.value);
  next.set(device.device_id, device);
  devices.value = next;
}

const { connected } = useLiveReadings(updateDevice);

onMounted(() => {
  refresh();
  refreshTimer = setInterval(refresh, REFRESH_INTERVAL);
});

onBeforeUnmount(() => clearInterval(refreshTimer));
</script>

<template>
  <div class="dashboard-head">
    <h1>Pomieszczenia</h1>
    <span class="live" :class="{ on: connected }">
      {{ connected ? "na żywo" : "łączenie…" }}
    </span>
  </div>

  <p v-if="error" class="error" role="alert">{{ error }}</p>
  <p v-else-if="loading" class="muted">Ładowanie…</p>
  <p v-else-if="!rooms.length" class="muted">Brak urządzeń. Uruchom collector lub symulatory.</p>

  <div class="rooms">
    <RoomCard v-for="item in rooms" :key="item.room" :room="item.room" :devices="item.devices" />
  </div>
</template>
