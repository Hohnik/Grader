-- Create the `submissions` table
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score TEXT NOT NULL,
    timestamp DATETIME,
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
    containerUrl TEXT NOT NULL
);
