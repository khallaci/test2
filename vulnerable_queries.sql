-- Example SQL queries that demonstrate unsafe patterns (for static analysis)
-- These are not exploitation payloads; they just show concatenation / interpolation issues.

-- 1) Unsafe dynamic SQL assembled by application code
-- (the application concatenates user input into the WHERE clause)
-- e.g. application builds: "SELECT * FROM products WHERE sku = '" || user_input || "'"

-- 2) Missing input sanitization before building an INSERT statement
-- an app might do: "INSERT INTO comments (user, body) VALUES ('" || username || "', '" || body || "')"

-- 3) Example of a query with no parameter placeholders (should prefer prepared statements)
SELECT * FROM orders WHERE order_date >= '2025-01-01';
