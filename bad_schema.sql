-- Schema file with an intentional syntax error for static-check detection
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
    email TEXT NOT NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- MISSING COMMA before this line (syntax error)
);

-- Another intentional issue: overly-permissive default role (not recommended for production)
-- GRANT ALL ON users TO PUBLIC;
