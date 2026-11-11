<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { fetchReadings } from "../api.js";
import { TYPE_LABELS, formatReading, roomLabel } from "../format.js";
import { RANGES, seriesFor, toPoint } from "../series.js";
import HistoryChart from "./HistoryChart.vue";

const props = defineProps({
  device: { type: Object, required: true },
});

const emit = defineEmits(["close"]);

const range = ref(RANGES[0]);
const points = ref({});
const loading = ref(false);
const error = ref("");
let requestId = 0;

const series = computed(() => seriesFor(props.device.type));
const current = computed(() => formatReading(props.device.type, props.device.last_reading?.data));
const isEmpty = computed(() => series.value.every((s) => !points.value[s.key]?.length));

function buildPoints(readings) {
  const result = {};
  for (const s of series.value) {
    result[s.key] = readings.map((reading) => toPoint(s, reading)).filter(Boolean);
  }
  return result;
}

async function load() {
  const id = ++requestId;
  loading.value = true;
  error.value = "";
  const from = new Date(Date.now() - range.value.hours * 3600 * 1000);
  try {
    const readings = await fetchReadings(props.device.device_id, { from, bucket: range.value.bucket });
    if (id === requestId) {
      points.value = buildPoints(readings);
    }
  } catch {
    if (id === requestId) {
      error.value = "Nie udało się pobrać historii.";
    }
  } finally {
    if (id === requestId) {
      loading.value = false;
    }
  }
}

function appendLive(reading) {
  if (range.value.bucket || !reading) {
    return;
  }
  const cutoff = Date.now() - range.value.hours * 3600 * 1000;
  const next = {};
  for (const s of series.value) {
    const list = (points.value[s.key] ?? []).filter((p) => p.x >= cutoff);
    const point = toPoint(s, reading);
    if (point && !list.some((p) => p.x === point.x)) {
      list.push(point);
    }
    next[s.key] = list;
  }
  points.value = next;
}

watch(() => props.device.device_id, load);
watch(range, load);
watch(
  () => props.device.last_reading?.ts,
  (ts, previous) => {
    if (ts && ts !== previous) {
      appendLive(props.device.last_reading);
    }
  },
);

function onKey(event) {
  if (event.key === "Escape") {
    emit("close");
  }
}

onMounted(() => {
  load();
  window.addEventListener("keydown", onKey);
});

onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <section class="card history" role="dialog" aria-modal="true" :aria-label="device.device_id">
      <header class="history-head">
        <div>
          <h2>{{ TYPE_LABELS[device.type] ?? device.type }}</h2>
          <span class="muted">{{ roomLabel(device.room) }} · {{ device.device_id }}</span>
        </div>
        <button class="link-button" type="button" @click="emit('close')">Zamknij</button>
      </header>

      <div class="history-bar">
        <span class="history-current">{{ current.join(" · ") }}</span>
        <div class="ranges" role="group" aria-label="Zakres">
          <button
            v-for="item in RANGES"
            :key="item.id"
            type="button"
            :class="{ active: item.id === range.id }"
            @click="range = item"
          >
            {{ item.label }}
          </button>
        </div>
      </div>

      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <p v-else-if="loading && isEmpty" class="muted">Ładowanie…</p>
      <p v-else-if="isEmpty" class="muted">Brak odczytów w wybranym zakresie.</p>
      <HistoryChart v-else :series="series" :points="points" />
    </section>
  </div>
</template>
