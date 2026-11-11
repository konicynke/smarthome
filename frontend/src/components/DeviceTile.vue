<script setup>
import { computed } from "vue";

import { TYPE_LABELS, formatReading, formatTime, isActive, isAlert } from "../format.js";

const props = defineProps({
  device: { type: Object, required: true },
});

defineEmits(["select"]);

const data = computed(() => props.device.last_reading?.data);
const values = computed(() => formatReading(props.device.type, data.value));
const alert = computed(() => isAlert(props.device.type, data.value));
const active = computed(() => isActive(props.device.type, data.value));
</script>

<template>
  <button
    type="button"
    class="device"
    :class="{ offline: !device.online, alert, active }"
    @click="$emit('select', device)"
  >
    <div class="device-head">
      <span class="device-type">{{ TYPE_LABELS[device.type] ?? device.type }}</span>
      <span class="badge" :class="device.source">{{ device.source === "real" ? "real" : "sim" }}</span>
    </div>
    <div class="device-values">
      <span v-for="value in values" :key="value">{{ value }}</span>
      <span v-if="!values.length" class="muted">brak odczytu</span>
    </div>
    <div class="device-foot">
      <span class="status" :class="device.online ? 'online' : 'offline'">
        {{ device.online ? "online" : "offline" }}
      </span>
      <span class="muted">{{ formatTime(device.last_reading?.ts) }}</span>
    </div>
    <div class="device-id muted">{{ device.device_id }}</div>
  </button>
</template>
