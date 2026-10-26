# NSE Stock Announcement Tracker — Database Design Guide

This guide contains:

1. Your **original SQL exactly as shared**.
2. An **improved version** ready to run in MySQL Workbench.
3. Simple explanations of **what changed, why, and what it improves**.
4. Example queries and guidance for your Python announcement tracker.

> **Recommended starting design:** Two physical tables (`stocks_list`, `stocks_data`) plus one calculated SQL view (`stocks_insights`). A view is appropriate for your first version because it avoids keeping manually maintained counts in sync.

---

## 1. Your original SQL (unchanged)

```sql
create table stocks_list(
	id int primary key not null auto_increment,
    symbol varchar(300) not null,
    stock_name varchar(400) not null
);

create table stocks_data(
	id int primary key not null auto_increment,
    stock_id int,
    annoucement_date date,
    file_url varchar(2001),
    file_text varchar(2000),
    subject varchar(500),
    file_size varchar(100),
    priority enum('P1','P2','P3','N1','N2','N3','C1','C2','C3') not null,
    foreign key (stock_id) references stocks_list(id)
);

create table stocks_insights(
	id int primary key not null auto_increment,
    stock_id int,
    announcements_count int,
    p1 int default 0,
    p2 int default 0,
    p3 int default 0,
    n1 int default 0,
    n2 int default 0,
    n3 int default 0,
    c1 int default 0,
    c2 int default 0,
    c3 int default 0,
    
    foreign key (stock_id) references stocks_list(id)
)
```

### What you designed correctly

- **Separate company details and announcements.** A company appears once in `stocks_list` and can have many records in `stocks_data`.
- **Use a primary key** (`id`) in each table to identify each row.
- **Use a foreign key** (`stock_id`) so announcements can be connected to the correct company.
- **Think about insights separately.** You want totals for each priority, which is useful for your dashboard.

---

## 2. Improved SQL — complete runnable version

> Run this in a **new/empty database**. It creates two tables and one view. It does **not** drop or modify your existing tables. If you already created the original tables, use a new schema for testing or plan a migration instead of running duplicate `CREATE TABLE` statements.

```sql
CREATE DATABASE IF NOT EXISTS nse_tracker;
USE nse_tracker;

-- TABLE 1: One row for each stock/company
CREATE TABLE stocks_list (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(30) NOT NULL UNIQUE,
    stock_name VARCHAR(400) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- TABLE 2: One row for each NSE announcement
CREATE TABLE stocks_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    nse_seq_id VARCHAR(30) NOT NULL UNIQUE,
    announcement_date DATETIME NOT NULL,
    file_url TEXT,
    announcement_text TEXT,
    subject VARCHAR(500),
    file_size VARCHAR(100),
    priority ENUM('P1','P2','P3','N1','N2','N3',
                  'C1','C2','C3') DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stock_announcement
        FOREIGN KEY (stock_id) REFERENCES stocks_list(id),

    INDEX idx_stock_date (stock_id, announcement_date),
    INDEX idx_priority_date (priority, announcement_date),
    INDEX idx_announcement_date (announcement_date)
) ENGINE=InnoDB;

-- VIEW 3: Counts are calculated from actual announcement rows
CREATE VIEW stocks_insights AS
SELECT
    s.id AS stock_id,
    s.symbol,
    s.stock_name,
    COUNT(d.id) AS announcements_count,
    SUM(CASE WHEN d.priority = 'P1' THEN 1 ELSE 0 END) AS p1,
    SUM(CASE WHEN d.priority = 'P2' THEN 1 ELSE 0 END) AS p2,
    SUM(CASE WHEN d.priority = 'P3' THEN 1 ELSE 0 END) AS p3,
    SUM(CASE WHEN d.priority = 'N1' THEN 1 ELSE 0 END) AS n1,
    SUM(CASE WHEN d.priority = 'N2' THEN 1 ELSE 0 END) AS n2,
    SUM(CASE WHEN d.priority = 'N3' THEN 1 ELSE 0 END) AS n3,
    SUM(CASE WHEN d.priority = 'C1' THEN 1 ELSE 0 END) AS c1,
    SUM(CASE WHEN d.priority = 'C2' THEN 1 ELSE 0 END) AS c2,
    SUM(CASE WHEN d.priority = 'C3' THEN 1 ELSE 0 END) AS c3
FROM stocks_list AS s
LEFT JOIN stocks_data AS d ON d.stock_id = s.id
GROUP BY s.id, s.symbol, s.stock_name;
```

**Why three indexes here?** They demonstrate three common tracker screens: company history, latest announcements by priority, and all announcements by date. Indexes take storage and slow down writes somewhat, so measure actual queries with `EXPLAIN` before keeping all of them at large scale.

---

## 3. Every change explained simply

| Original | Updated | Why change it? | What improves? |
|---|---|---|---|
| `symbol VARCHAR(300)` | `symbol VARCHAR(30)` | Stock symbols are much shorter than 300 characters. | More sensible limit; prevents unusually long values. |
| `symbol` without `UNIQUE` | `symbol ... UNIQUE` | You should not have two master rows for the same symbol. | Prevents accidental duplicate stocks. |
| No `created_at` | Added `created_at` | You may want to know when your tracker saved a record. | Easier debugging and record tracking. |
| `stocks_data.id INT` | `BIGINT` | Announcement history may grow for years. | Higher row-ID capacity (optional future-proofing; `INT` is adequate for many projects). |
| `stock_id INT` | `stock_id INT NOT NULL` | Every announcement should point to a known stock. | Stops announcements without a company reference. |
| No NSE announcement identifier | `nse_seq_id VARCHAR(30) NOT NULL UNIQUE` | The API can return the same announcement in repeated polling. | Helps avoid inserting duplicates. Confirm `seq_id` is unique in the feed you use. |
| `annoucement_date DATE` | `announcement_date DATETIME` | Corrects spelling and saves both date and time. | Better chronological sorting and market-hours analysis. |
| `file_url VARCHAR(2001)` | `file_url TEXT` | Document URLs can vary in length. | Flexible URL storage. `VARCHAR(2048)` is also a reasonable option when you want a clear length limit. |
| `file_text VARCHAR(2000)` | `announcement_text TEXT` | Announcement descriptions can exceed 2,000 characters. | More room, and a clearer name for API announcement text. |
| `priority ... NOT NULL` | `priority ... DEFAULT NULL` | A newly fetched announcement may not be classified yet. | You can save the announcement first and classify it later. |
| No explicitly named foreign key | `CONSTRAINT fk_stock_announcement ...` | A readable constraint name helps identify the rule. | Easier database maintenance; **the short `FOREIGN KEY ... REFERENCES ...` version works equally well**. |
| No query-specific indexes | Added composite/date indexes | Many queries filter by stock, priority or date. | Potentially faster searches and sorting. |
| No storage engine specified | `ENGINE=InnoDB` | Makes the intended engine explicit. | Transaction support, foreign key enforcement and crash recovery. (InnoDB is already the usual MySQL default.) |
| Stored `stocks_insights` table | Calculated `stocks_insights` VIEW | Manually saved counts become stale unless every write updates them too. | Counts always reflect the underlying announcement records when queried. |

### A note about `file_size`

I kept `file_size VARCHAR(100)` because NSE may return values such as `383.34 KB`. For analytics, a **numeric column containing bytes** is better, such as `file_size_bytes BIGINT UNSIGNED`, if your Python code converts the API string into bytes. Then you can sort and compare file sizes numerically. You could keep the original text too if you want to preserve the API value.

### A note about `subject` and `announcement_text`

For the NSE example you provided earlier:

- `desc` (for example, `Commencement of commercial production/operations`) can map to `subject`.
- `attchmntText` (the longer description) can map to `announcement_text`.
- `attchmntFile` maps to `file_url`.
- `sort_date` maps to `announcement_date`.
- `seq_id` maps to `nse_seq_id`.

The `announcement_text` field in this schema is **not** the entire extracted PDF text. Keep full PDF extraction and AI summaries separate later if needed.

---

## 4. Foreign key, index and engine — very simple explanation

### Foreign key

```sql
FOREIGN KEY (stock_id) REFERENCES stocks_list(id)
```

This means a `stocks_data.stock_id` must point to an existing `stocks_list.id` (and here `stock_id` cannot be `NULL`). If stock ID 99 does not exist, inserting an announcement for stock ID 99 fails.

You can use either:

```sql
FOREIGN KEY (stock_id) REFERENCES stocks_list(id)
```

or:

```sql
CONSTRAINT fk_stock_announcement
    FOREIGN KEY (stock_id) REFERENCES stocks_list(id)
```

Both enforce the same rule. The second simply gives the rule your own name.

### Composite index

```sql
INDEX idx_stock_date (stock_id, announcement_date)
```

Think of a book sorted first by **company**, then by **date**. It makes finding SILKFLEX's latest announcements easier. Column order matters: this index is most useful when your query starts with `stock_id`.

### Priority-and-date index

```sql
INDEX idx_priority_date (priority, announcement_date)
```

Useful for queries such as “show the 20 newest P1 announcements.” An index on priority alone may be less useful because there are only nine priority values.

### Date index

```sql
INDEX idx_announcement_date (announcement_date)
```

Useful for searching a date range **across all companies**, rather than for one specific stock.

### Storage engine

```sql
ENGINE=InnoDB
```

InnoDB is the MySQL storage engine that manages table data, indexes, transactions (`COMMIT`/`ROLLBACK`) and foreign keys.

**Apartment analogy:** `stocks_list` is the building's flat register; `stocks_data` is the activity register; a foreign key ensures each activity belongs to a real flat; an index is a sorted filing system; InnoDB is the records-management system that keeps everything consistent.

---

## 5. Why a VIEW for stocks_insights?

Your original `stocks_insights` was a physical table with `p1`, `p2` and other stored counters.

Problem: when you insert a new P1 announcement or change a record from P2 to P1, you must also update the counters. If the code forgets, your dashboard becomes inaccurate.

A view runs a calculation using the actual rows every time you query it:

```sql
SELECT *
FROM stocks_insights
WHERE symbol = 'SILKFLEX';
```

**Benefits:** no duplicated count data, simpler Python code, and automatically up-to-date counts.

**Trade-off:** a normal MySQL view does not cache these counts. It can be slower with very large datasets; a physical summary table may be useful later.

> In your original physical `stocks_insights` table, `stock_id` was not `UNIQUE`, so one company could accidentally have multiple summary rows. If you ever return to a stored summary table, add `UNIQUE(stock_id)` and update counts inside a reliable transaction or scheduled aggregation job.

---

## 6. Example: Insert NSE data safely

```sql
-- Insert stock master record first
INSERT INTO stocks_list (symbol, stock_name)
VALUES ('SILKFLEX', 'Silkflex Polymers (India) Limited');

-- Use its ID to create an announcement
INSERT INTO stocks_data (
    stock_id, nse_seq_id, announcement_date,
    file_url, announcement_text, subject, file_size, priority
)
SELECT
    id,
    '106821963',
    '2026-10-19 15:48:02',
    'https://nsearchives.nseindia.com/corporate/SILKFLEX_19102026154705_Letter.pdf',
    'Intimation regarding commencement of commercial production for in-house manufacturing of textile garment printing inks and expansion of manufacturing capabilities.',
    'Commencement of commercial production/operations',
    '383.34 KB',
    NULL
FROM stocks_list
WHERE symbol = 'SILKFLEX';

-- Later: assign the classification
UPDATE stocks_data
SET priority = 'P1'
WHERE nse_seq_id = '106821963';

-- Company-level counts
SELECT *
FROM stocks_insights
WHERE symbol = 'SILKFLEX';
```

The P1 assignment above is **only a coding demonstration**, not a real investment classification of the announcement.

For Python ingestion, avoid inserting the same `nse_seq_id` twice: handle duplicate-key errors deliberately or use a carefully chosen upsert (`INSERT ... ON DUPLICATE KEY UPDATE`). Don't silently ignore unexpected database errors.

---

## 7. Useful queries for your tracker

### Latest announcements for a company

```sql
SELECT d.*
FROM stocks_data AS d
JOIN stocks_list AS s ON s.id = d.stock_id
WHERE s.symbol = 'SILKFLEX'
ORDER BY d.announcement_date DESC
LIMIT 20;
```

### Latest P1 announcements across all stocks

```sql
SELECT s.symbol, d.subject, d.announcement_date
FROM stocks_data AS d
JOIN stocks_list AS s ON s.id = d.stock_id
WHERE d.priority = 'P1'
ORDER BY d.announcement_date DESC
LIMIT 20;
```

### All announcements on October 19, 2026

```sql
SELECT *
FROM stocks_data
WHERE announcement_date >= '2026-10-19'
  AND announcement_date < '2026-10-20';
```

Using a date range like this keeps the filter suitable for an index on `announcement_date`.

### Check whether MySQL uses your index

```sql
EXPLAIN
SELECT *
FROM stocks_data
WHERE stock_id = 1
ORDER BY announcement_date DESC;
```

Inspect `key` and `type` in the results. MySQL's optimiser selects the execution plan; creating an index doesn't guarantee it will always be used.

---

## 8. Optional improvements for later versions

These are helpful but **not required** for your first version:

1. **Category field/table:** Store the type of announcement (for example, business growth, financial results, regulatory issue) separately from priority (`P1`, `N1`, etc.). A lookup table is useful when categories need controlled names.
2. **Processing status:** Add a status such as `pending`, `classified`, or `failed` if an AI classifier processes announcements asynchronously.
3. **Document analysis:** Store extracted PDF text, AI summary and classification reasoning in a separate analysis table if you need them; avoid confusing API descriptions with full PDF text.
4. **Time window for insights:** Decide whether counts mean **all-time** or **last 30/90/365 days**; a view shown here is all-time.
5. **Symbol history:** If NSE symbols change, consider keeping an exchange identifier and a symbol-history table later.
6. **Data quality:** Decide how to handle announcements with missing/duplicate `seq_id`; the recommended schema requires an ID, so your Python program should validate it before inserting.
7. **Data security:** Keep database passwords outside Python source code and avoid placing sensitive credentials in repositories.
8. **Indexes:** Indexes speed some reads but cost storage and write time. Measure real queries before adding more.

---

## 9. Final recommendation

Start with:

- `stocks_list` — **real table**, one company per row.
- `stocks_data` — **real table**, one NSE announcement per row.
- `stocks_insights` — **view**, calculates counts from the announcements.

**Build this first**, fetch and insert announcements with Python, add priority classification, then build your dashboard. If dashboard performance becomes a problem, consider a maintained summary table later.
