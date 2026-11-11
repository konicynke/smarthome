CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    room      TEXT NOT NULL,
    type      TEXT NOT NULL,
    source    TEXT NOT NULL CHECK (source IN ('real', 'sim')),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS readings (
    id        BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    ts        TIMESTAMPTZ NOT NULL DEFAULT now(),
    data      JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS readings_device_ts ON readings (device_id, ts DESC);

CREATE TABLE IF NOT EXISTS users (
    id            BIGSERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
