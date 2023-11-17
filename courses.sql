CREATE TABLE teachers
        (
            id                  INTEGER PRIMARY KEY,
            name                TEXT
        );
        CREATE TABLE courses
        (
            id                  INTEGER PRIMARY KEY,
            name                TEXT,
            credits             INTEGER,
            teacher_id          INTEGER REFERENCES teachers(id)
        );
        CREATE TABLE teachers_courses
        (
            id                  INTEGER PRIMARY KEY,
            teacher_id          INTEGER REFERENCES teachers(id),
            course_id           INTEGER REFERENCES courses(id)
        );
        CREATE TABLE students
        (
            id                  INTEGER PRIMARY KEY,
            name                TEXT
        );
    
        CREATE TABLE course_performance
        (
            id                  INTEGER PRIMARY KEY,
            student_id          INTEGER REFERENCES students(id),
            course_id           INTEGER REFERENCES courses(id),
            grade               INTEGER,
            date                DATE
        );
        CREATE TABLE groups
        (
            id                  INTEGER PRIMARY KEY,
            name                TEXT
        );
        CREATE TABLE teachers_groups
        (
            id                  INTEGER PRIMARY KEY,
            teacher_id          INTEGER REFERENCES teachers(id),
            group_id            INTEGER REFERENCES groups(id)
        );
        CREATE TABLE students_groups
        (
            id                  INTEGER PRIMARY KEY,
            student_id          INTEGER REFERENCES students(id),
            group_id            INTEGER REFERENCES groups(id)
        );