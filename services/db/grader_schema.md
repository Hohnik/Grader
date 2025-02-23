# Grader Schema

## Tables

### 1. `assignments`
This table holds the global assignment IDs that count up automatically.

| Column Name    | Data Type    | Constraints     |
|----------------|--------------|-----------------|
| `id`           | INTEGER      | PRIMARY KEY, AUTOINCREMENT |

---

### 2. `students`
This table stores information about students.

| Column Name    | Data Type    | Constraints     |
|----------------|--------------|-----------------|
| `id`           | INTEGER      | PRIMARY KEY, AUTOINCREMENT |
| `username`     | TEXT         | UNIQUE, NOT NULL |

---

### 3. `courses`
This table stores information about courses.

| Column Name    | Data Type    | Constraints     |
|----------------|--------------|-----------------|
| `id`           | INTEGER      | PRIMARY KEY, AUTOINCREMENT |
| `coursename`   | TEXT         | UNIQUE, NOT NULL |
| `containerUrl` | TEXT         | NOT NULL |
