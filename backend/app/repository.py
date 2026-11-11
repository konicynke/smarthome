from psycopg2.extras import Json


def upsert_device(cur, device_id, room, type_, source):
    cur.execute(
        """
        INSERT INTO devices (device_id, room, type, source)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (device_id) DO UPDATE
        SET room = EXCLUDED.room,
            type = EXCLUDED.type,
            source = EXCLUDED.source,
            last_seen = now()
        """,
        (device_id, room, type_, source),
    )


def insert_reading(cur, device_id, values):
    cur.execute(
        "INSERT INTO readings (device_id, data) VALUES (%s, %s)",
        (device_id, Json(values)),
    )


def list_devices(cur, online_timeout_seconds, device_id=None):
    cur.execute(
        """
        SELECT d.device_id, d.room, d.type, d.source, d.last_seen,
               d.last_seen > now() - make_interval(secs => %(timeout)s) AS online,
               r.ts AS last_ts, r.data AS last_data
        FROM devices d
        LEFT JOIN LATERAL (
            SELECT ts, data FROM readings
            WHERE device_id = d.device_id
            ORDER BY ts DESC
            LIMIT 1
        ) r ON true
        WHERE %(device_id)s::text IS NULL OR d.device_id = %(device_id)s::text
        ORDER BY d.room, d.device_id
        """,
        {"timeout": online_timeout_seconds, "device_id": device_id},
    )
    devices = []
    for row in cur.fetchall():
        last_ts = row.pop("last_ts")
        last_data = row.pop("last_data")
        row["last_reading"] = (
            None if last_ts is None else {"ts": last_ts, "data": last_data}
        )
        devices.append(row)
    return devices


def get_device(cur, device_id, online_timeout_seconds):
    devices = list_devices(cur, online_timeout_seconds, device_id)
    return devices[0] if devices else None


def get_readings(cur, device_id, ts_from, ts_to, limit):
    cur.execute(
        """
        SELECT ts, data FROM (
            SELECT ts, data FROM readings
            WHERE device_id = %(device_id)s
              AND (%(ts_from)s::timestamptz IS NULL OR ts >= %(ts_from)s::timestamptz)
              AND (%(ts_to)s::timestamptz IS NULL OR ts <= %(ts_to)s::timestamptz)
            ORDER BY ts DESC
            LIMIT %(limit)s
        ) latest
        ORDER BY ts ASC
        """,
        {"device_id": device_id, "ts_from": ts_from, "ts_to": ts_to, "limit": limit},
    )
    return cur.fetchall()