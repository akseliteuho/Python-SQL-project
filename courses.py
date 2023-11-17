import os
import os.path
import sqlite3

# poistaa tietokannan alussa (kätevä moduulin testailussa)
if os.path.exists("courses.db"):
    os.remove("courses.db")

db = sqlite3.connect("courses.db")
db.isolation_level = None

# luo tietokantaan tarvittavat taulut
def create_tables():
    db.executescript("""
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
""")
    
# lisää opettajan tietokantaan
def create_teacher(name):
    sql = "INSERT INTO teachers(name) VALUES (?)"
    id = db.execute(sql, [name]).lastrowid
    return id

# lisää kurssin tietokantaan, ottaen huomioon kurssin opettajat(=lista opettajien id:itä)
def create_course(name, credits, teacher_ids):
    sql = "INSERT INTO courses(name, credits) VALUES (?, ?)"
    id = db.execute(sql, [name, credits]).lastrowid
    sql = "INSERT INTO teachers_courses(teacher_id, course_id) VALUES (?, ?)"
    db.executemany(sql, [(teacher_id, id) for teacher_id in teacher_ids])
    return id

# lisää opiskelijan tietokantaan
def create_student(name):
    sql = "INSERT INTO students(name) VALUES (?)"
    id = db.execute(sql, [name]).lastrowid
    return id

# antaa opiskelijalle suorituksen kurssista
def add_credits(student_id, course_id, date, grade):
    sql = "INSERT INTO course_performance(student_id, course_id, date, grade) VALUES (?, ?, ?, ?)"
    db.execute(sql, [student_id, course_id, date, grade])

# lisää ryhmän tietokantaan
def create_group(name, teacher_ids, student_ids):
    sql = "INSERT INTO groups(name) VALUES (?)"
    id = db.execute(sql, [name]).lastrowid
    sql = "INSERT INTO teachers_groups(teacher_id, group_id) VALUES (?, ?)"
    db.executemany(sql, [(teacher_id, id) for teacher_id in teacher_ids])
    sql = "INSERT INTO students_groups(student_id, group_id) VALUES (?, ?)"
    db.executemany(sql, [(student_id, id) for student_id in student_ids])
    return id

# hakee kurssit, joissa opettaja opettaa (aakkosjärjestyksessä)
def courses_by_teacher(teacher_name):
    sql = """SELECT courses.name
                FROM courses, teachers, teachers_courses
                WHERE courses.id = teachers_courses.course_id
                AND teachers.id = teachers_courses.teacher_id
                AND teachers.name = ?
                ORDER BY courses.name
                """
    res = db.execute(sql, [teacher_name]).fetchall()
    return [rivi[0] for rivi in res]

# hakee opettajan antamien opintopisteiden määrän
def credits_by_teacher(teacher_name):
    sql = """SELECT SUM(courses.credits)
                FROM courses, teachers, teachers_courses, course_performance
                WHERE courses.id = teachers_courses.course_id
                AND teachers.id = teachers_courses.teacher_id
                AND courses.id = course_performance.course_id
                AND teachers.name = ?
                """
    res = db.execute(sql, [teacher_name]).fetchone()[0]
    return res

# hakee opiskelijan suorittamat kurssit arvosanoineen (aakkosjärjestyksessä)
def courses_by_student(student_name):
    sql = """ SELECT courses.name, course_performance.grade
                FROM courses, students, course_performance
                WHERE courses.id = course_performance.course_id
                AND students.id = course_performance.student_id
                AND students.name = ?
                ORDER BY courses.name
                """
    res = db.execute(sql, [student_name]).fetchall()
    return res

# hakee tiettynä vuonna saatujen opintopisteiden määrän
def credits_by_year(year):
    sql = """SELECT SUM(courses.credits)
                FROM courses, course_performance
                WHERE courses.id = course_performance.course_id
                AND course_performance.date LIKE ?
                """
    res = db.execute(sql, [str(year) + "%"]).fetchone()[0]
    return res

# hakee kurssin arvosanojen jakauman sanakirja muodossa (järjestyksessä arvosanat 1-5)
def grade_distribution(course_name):
    sql = """SELECT course_performance.grade, COUNT(course_performance.grade)
                FROM course_performance
                LEFT JOIN courses ON course_performance.course_id = courses.id
                AND courses.name = ?
                GROUP BY course_performance.grade
                """
    res = db.execute(sql, [course_name]).fetchall()
    return {rivi[0]: rivi[1] for rivi in res}

# hakee listan kursseista (nimi, opettajien määrä, suorittajien määrä) (aakkosjärjestyksessä)
def course_list():
    sql = """SELECT courses.name, COUNT(DISTINCT teachers.id), COUNT(DISTINCT course_performance.student_id)
                FROM courses
                LEFT JOIN teachers_courses ON courses.id = teachers_courses.course_id
                LEFT JOIN teachers ON teachers_courses.teacher_id = teachers.id
                LEFT JOIN course_performance ON courses.id = course_performance.course_id
                GROUP BY courses.name
                ORDER BY courses.name
                """
    res = db.execute(sql).fetchall()
    return res

# hakee listan opettajista kursseineen (aakkosjärjestyksessä opettajat ja kurssit)
def teacher_list():
    sql =   """SELECT teachers.name, courses.name
                FROM teachers, courses, teachers_courses
                WHERE teachers.id = teachers_courses.teacher_id
                AND courses.id = teachers_courses.course_id
                ORDER BY teachers.name, courses.name
                """
    res = db.execute(sql).fetchall()
    teacher_courses = {}
    for teacher, course in res:
        if teacher not in teacher_courses:
            teacher_courses[teacher] = []
        teacher_courses[teacher].append(course)

    result = [(teacher, courses) for teacher, courses in teacher_courses.items()]

    return result

# hakee ryhmässä olevat henkilöt, opiskelijat ja opettajat (aakkosjärjestyksessä)
def group_people(group_name):
    sql = """SELECT students.name
                FROM students, groups, students_groups
                WHERE students.id = students_groups.student_id
                AND groups.id = students_groups.group_id
                AND groups.name = ?
                UNION
                SELECT teachers.name
                FROM teachers, groups, teachers_groups
                WHERE teachers.id = teachers_groups.teacher_id
                AND groups.id = teachers_groups.group_id
                AND groups.name = ?
                ORDER BY students.name
                """
    res = db.execute(sql, [group_name, group_name]).fetchall()
    return [rivi[0] for rivi in res]

# hakee ryhmissä saatujen opintopisteiden määrät, myös jos opintopisteiden määrä on 0 (aakkosjärjestyksessä)
def credits_in_groups():
    sql = """SELECT groups.name, IFNULL(SUM(courses.credits), 0)
                FROM groups
                LEFT JOIN students_groups ON groups.id = students_groups.group_id
                LEFT JOIN course_performance ON students_groups.student_id = course_performance.student_id
                LEFT JOIN courses ON course_performance.course_id = courses.id
                GROUP BY groups.name
                ORDER BY groups.name;
                """
    res = db.execute(sql).fetchall()
    return res

# hakee ryhmät, joissa on tietty opettaja ja opiskelija (aakkosjärjestyksessä)
def common_groups(teacher_name, student_name):
    sql = """SELECT groups.name
                FROM groups, teachers, teachers_groups, students, students_groups
                WHERE groups.id = teachers_groups.group_id
                AND teachers.id = teachers_groups.teacher_id
                AND groups.id = students_groups.group_id
                AND students.id = students_groups.student_id
                AND teachers.name = ?
                AND students.name = ?
                ORDER BY groups.name
                """
    res = db.execute(sql, [teacher_name, student_name]).fetchall()
    return [rivi[0] for rivi in res]