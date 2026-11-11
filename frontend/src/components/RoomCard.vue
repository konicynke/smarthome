<script setup>
import { computed } from "vue";

import { roomLabel } from "../format.js";
import DeviceTile from "./DeviceTile.vue";

const props = defineProps({
  room: { type: String, required: true },
  devices: { type: Array, required: true },
});

defineEmits(["select"]);

const onlineCount = computed(() => props.devices.filter((device) => device.online).length);
</script>

<template>
  <section class="card room">
    <header class="room-head">
      <h2>{{ roomLabel(room) }}</h2>
      <span class="muted">{{ onlineCount }}/{{ devices.length }} online</span>
    </header>
    <div class="devices">
      <DeviceTile
        v-for="device in devices"
        :key="device.device_id"
        :device="device"
        @select="$emit('select', $event)"
      />
    </div>
  </section>
</template>
