CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    type TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    salary_range TEXT,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    benefits TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_experience_level
ON jobs(experience_level);
