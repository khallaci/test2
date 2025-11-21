-- ============================================================
-- Example SQL queries that demonstrate *unsafe patterns*
-- for static analysis tools like CodeRabbit.
-- These are NOT malicious payloads. They only illustrate
-- bad practices such as string concatenation, no parameters,
-- or missing sanitization.
-- ============================================================

-- 1) Dynamic SQL built via concatenation (unsafe in real apps)
-- Example: application code builds something like:
-- "SELECT * FROM users WHERE username = '" + userInput + "';"
-- Code review tools should flag this as SQL injection risk.
SELECT * FROM users WHERE username = ' + user_input + ';

-- 2) Unsafe INSERT example with unescaped values
-- Applications should NOT build INSERT statements like this:
-- "INSERT INTO logs (level, msg) VALUES ('" + lvl + "', '" + msg + "')"
INSERT INTO logs (level, message)
VALUES (' + logLevel + ', ' + logMessage + ');

-- 3) Query executed without prepared statements or placeholders
-- Tools may warn that this should use parameters.
SELECT * FROM orders
WHERE customer_id = ' + customerId + ';

-- 4) LIKE pattern assembled directly from user input
-- Another typical SQL‑injection‑risk pattern.
SELECT * FROM products
WHERE name LIKE '%" + searchTerm + "%';

-- 5) UPDATE statement interpolating external input
UPDATE accounts
SET email = ' + newEmail + '
WHERE id = ' + accountId + ';

-- 6) DELETE query with no validation (very risky pattern)
DELETE FROM sessions
WHERE session_id = ' + session + ';

-- 7) A normal query (no injection risk — should NOT be flagged)
SELECT * FROM orders WHERE order_date >= '2025-01-01';
