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

def get_bucketed_readings(cur, device_id, ts_from, ts_to, bucket_seconds, limit):
    cur.execute(
        """
        SELECT ts, data FROM (
            SELECT bucket AS ts, jsonb_object_agg(key, value) AS data
            FROM (
                SELECT bucket, key,
                       COALESCE(
                           to_jsonb(round(avg(num), 2)),
                           to_jsonb(bool_or(flag))
                       ) AS value
                FROM (
                    SELECT date_bin(make_interval(secs => %(bucket)s), r.ts,
                                    'epoch'::timestamptz) AS bucket,
                           kv.key,
                           CASE WHEN jsonb_typeof(kv.value) = 'number'
                                THEN (kv.value #>> '{}')::numeric END AS num,
                           CASE WHEN jsonb_typeof(kv.value) = 'boolean'
                                THEN (kv.value #>> '{}')::boolean END AS flag
                    FROM readings r
                    CROSS JOIN LATERAL jsonb_each(r.data) kv
                    WHERE r.device_id = %(device_id)s
                      AND (%(ts_from)s::timestamptz IS NULL OR r.ts >= %(ts_from)s::timestamptz)
                      AND (%(ts_to)s::timestamptz IS NULL OR r.ts <= %(ts_to)s::timestamptz)
                ) points
                GROUP BY bucket, key
            ) per_key
            WHERE value IS NOT NULL
            GROUP BY bucket
            ORDER BY bucket DESC
            LIMIT %(limit)s
        ) latest
        ORDER BY ts ASC
        """,
        {
            "device_id": device_id,
            "ts_from": ts_from,
            "ts_to": ts_to,
            "bucket": bucket_seconds,
            "limit": limit,
        },
    )
    return cur.fetchall()

def get_user(cur, username):
    cur.execute(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username,),
    )
    return cur.fetchone()


def create_user(cur, username, password_hash):
    cur.execute(
        """
        INSERT INTO users (username, password_hash) VALUES (%s, %s)
        ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
        """,
        (username, password_hash),
    )
