CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY,
    ts          TEXT    NOT NULL,
    source      TEXT    NOT NULL,
    session_id  TEXT,
    cwd         TEXT,
    kind        TEXT,
    command     TEXT,
    exit_code   INTEGER,
    duration_ms INTEGER,
    payload     TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_ts     ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_exit   ON events(exit_code);
CREATE INDEX IF NOT EXISTS idx_events_sess   ON events(session_id);
