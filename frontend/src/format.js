export const TYPE_LABELS = {
  temp_humidity: "Temperatura i wilgotność",
  illuminance: "Natężenie światła",
  motion: "Czujnik ruchu",
  gas: "Czujnik gazu",
};

export const ROOM_LABELS = {
  kitchen: "Kuchnia",
  bedroom: "Sypialnia",
  rpi_room: "Pokój (Raspberry Pi)",
};

export function roomLabel(room) {
  return ROOM_LABELS[room] ?? room;
}

function number(value, digits = 1) {
  return typeof value === "number"
    ? value.toLocaleString("pl-PL", { maximumFractionDigits: digits })
    : "–";
}

export function formatReading(type, data) {
  if (!data) {
    return [];
  }
  switch (type) {
    case "temp_humidity":
      return [`${number(data.temperature)} °C`, `${number(data.humidity, 0)} %`];
    case "illuminance":
      return [`${number(data.illuminance, 0)} lx`];
    case "motion":
      return [data.motion ? "Wykryto ruch" : "Brak ruchu"];
    case "gas":
      return [data.detected ? "Wykryto gaz!" : "W normie"];
    default:
      return Object.entries(data).map(([key, value]) => `${key}: ${value}`);
  }
}

export function isAlert(type, data) {
  return Boolean(data) && ((type === "gas" && data.detected) || (type === "motion" && data.motion));
}

export function formatTime(ts) {
  if (!ts) {
    return "brak danych";
  }
  const date = new Date(ts);
  const sameDay = date.toDateString() === new Date().toDateString();
  return sameDay
    ? date.toLocaleTimeString("pl-PL")
    : date.toLocaleString("pl-PL", { dateStyle: "short", timeStyle: "medium" });
}
