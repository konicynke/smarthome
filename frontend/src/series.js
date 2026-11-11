export const RANGES = [
  { id: "1h", label: "1 h", hours: 1, bucket: null },
  { id: "6h", label: "6 h", hours: 6, bucket: null },
  { id: "24h", label: "24 h", hours: 24, bucket: 60 },
  { id: "7d", label: "7 dni", hours: 24 * 7, bucket: 600 },
];

const SERIES = {
  temp_humidity: [
    { key: "temperature", label: "Temperatura [°C]", color: "#ef4444", axis: "y" },
    { key: "humidity", label: "Wilgotność [%]", color: "#3b82f6", axis: "y1" },
  ],
  illuminance: [{ key: "illuminance", label: "Natężenie światła [lx]", color: "#f59e0b", axis: "y" }],
  motion: [{ key: "motion", label: "Ruch", color: "#8b5cf6", axis: "y", binary: true }],
  gas: [{ key: "detected", label: "Gaz", color: "#dc2626", axis: "y", binary: true }],
};

export function seriesFor(type) {
  return SERIES[type] ?? [];
}

export function toPoint(series, reading) {
  const value = reading.data?.[series.key];
  if (value === undefined || value === null) {
    return null;
  }
  return { x: new Date(reading.ts).getTime(), y: series.binary ? Number(Boolean(value)) : value };
}
