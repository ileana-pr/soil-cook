-- local stores you can call or visit.
-- one row per store. id matches the number already used in the app.
CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT '',
  address TEXT NOT NULL DEFAULT '',
  phone TEXT NOT NULL DEFAULT '',
  website TEXT,
  hours TEXT NOT NULL DEFAULT '',
  miles REAL,
  ask_about TEXT NOT NULL DEFAULT ''
);

-- your own numbers and notes.
-- one row per section of the app. value is json text.
-- allowed keys: plan, prices, premix, calls, quotes, tests
CREATE TABLE IF NOT EXISTS user_data (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
