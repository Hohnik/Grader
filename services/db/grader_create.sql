-- Create the `assignments` table
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT
);

-- Create the `students` table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
);

-- Create the `courses` table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coursename TEXT UNIQUE NOT NULL,
    dockerfile TEXT NOT NULL,
    tests TEXT NOT NULL
);
