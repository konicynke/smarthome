<script setup>
import {
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  TimeScale,
  Tooltip,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { pl } from "date-fns/locale";
import { computed } from "vue";
import { Line } from "vue-chartjs";

ChartJS.register(LinearScale, TimeScale, PointElement, LineElement, Tooltip, Legend, Filler);

const props = defineProps({
  series: { type: Array, required: true },
  points: { type: Object, required: true },
});

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

const binary = computed(() => props.series.some((s) => s.binary));
const dualAxis = computed(() => props.series.some((s) => s.axis === "y1"));

const chartData = computed(() => ({
  datasets: props.series.map((s) => ({
    label: s.label,
    data: props.points[s.key] ?? [],
    borderColor: s.color,
    backgroundColor: `${s.color}33`,
    yAxisID: s.axis,
    stepped: s.binary ? "before" : false,
    fill: s.binary,
    pointRadius: 0,
    borderWidth: 2,
    tension: s.binary ? 0 : 0.25,
  })),
}));

const chartOptions = computed(() => {
  const text = cssVar("--muted");
  const grid = cssVar("--border");
  const yesNo = (value) => (value === 1 ? "tak" : value === 0 ? "nie" : "");
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    parsing: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { labels: { color: text } },
      tooltip: {
        callbacks: binary.value
          ? { label: (ctx) => `${ctx.dataset.label}: ${yesNo(ctx.parsed.y)}` }
          : {},
      },
    },
    scales: {
      x: {
        type: "time",
        adapters: { date: { locale: pl } },
        time: {
          tooltipFormat: "d MMM yyyy, HH:mm:ss",
          displayFormats: {
            second: "HH:mm:ss",
            minute: "HH:mm",
            hour: "HH:mm",
            day: "d MMM",
          },
        },
        ticks: { color: text, maxRotation: 0, autoSkipPadding: 16 },
        grid: { color: grid },
      },
      y: binary.value
        ? { min: 0, max: 1, ticks: { stepSize: 1, color: text, callback: yesNo }, grid: { color: grid } }
        : { ticks: { color: text }, grid: { color: grid } },
      ...(dualAxis.value
        ? { y1: { position: "right", ticks: { color: text }, grid: { drawOnChartArea: false } } }
        : {}),
    },
  };
});
</script>

<template>
  <div class="chart">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
