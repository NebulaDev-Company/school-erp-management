import sqlite3
from datetime import datetime

def create_connection():
    conn = sqlite3.connect("school.db")
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            birthdate TEXT,
            parent_phone TEXT,
            registration_date TEXT,
            archived INTEGER DEFAULT 0  -- ✅ أضف هذا السطر
        )
    ''')
    conn.commit()
    conn.close()


def get_all_students(archived_only=False):
    conn = create_connection()
    cursor = conn.cursor()
    if archived_only:
        cursor.execute("SELECT * FROM students WHERE archived = 1")
    else:
        cursor.execute("SELECT * FROM students WHERE archived = 0")
    students = cursor.fetchall()
    conn.close()
    return students



def update_student(student_id, name, class_, birthdate, parent_phone):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE students
        SET name = ?, class = ?, birthdate = ?, parent_phone = ?
        WHERE id = ?
    ''', (name, class_, birthdate, parent_phone, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def create_payment_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            amount REAL,
            date TEXT,
            note TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_payment(student_id, amount, date, note):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (student_id, amount, date, note)
        VALUES (?, ?, ?, ?)
    ''', (student_id, amount, date, note))
    conn.commit()
    conn.close()

def get_all_payments():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT students.name, payments.amount, payments.date, payments.note
        FROM payments
        JOIN students ON students.id = payments.student_id
        ORDER BY payments.date DESC
    ''')
    payments = cursor.fetchall()
    conn.close()
    return payments

def get_total_payments_per_student():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT students.id, students.name, IFNULL(SUM(payments.amount), 0) as total
        FROM students
        LEFT JOIN payments ON students.id = payments.student_id
        GROUP BY students.id
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def get_students_without_payments():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT students.id, students.name, students.class, students.birthdate, students.parent_phone
        FROM students
        LEFT JOIN payments ON students.id = payments.student_id
        WHERE payments.id IS NULL
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

import datetime

def get_students_missing_payment_this_month():
    conn = create_connection()
    cursor = conn.cursor()

    current_month = datetime.datetime.now().strftime("%Y-%m")  

    cursor.execute('''
        SELECT s.id, s.name, s.class, s.birthdate, s.parent_phone
        FROM students s
        WHERE NOT EXISTS (
            SELECT 1 FROM payments p
            WHERE p.student_id = s.id AND strftime('%Y-%m', p.date) = ?
        )
    ''', (current_month,))
    
    result = cursor.fetchall()
    conn.close()
    return result

def get_payments_by_month(month, year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT students.name, payments.amount, payments.date, payments.note
        FROM payments
        JOIN students ON payments.student_id = students.id
        WHERE strftime('%m', payments.date) = ? AND strftime('%Y', payments.date) = ?
    """, (f"{int(month):02d}", str(year)))
    results = cursor.fetchall()
    conn.close()
    return results

def get_monthly_total(month, year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount) FROM payments
        WHERE strftime('%m', payments.date) = ? AND strftime('%Y', payments.date) = ?
    """, (f"{int(month):02d}", str(year)))
    result = cursor.fetchone()[0]
    return result or 0.0

def get_yearly_total(year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount) FROM payments
        WHERE strftime('%Y', payments.date) = ?
    """, (str(year),))
    result = cursor.fetchone()[0]
    return result or 0.0

def get_monthly_income_by_year(year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%m', date) AS month, SUM(amount)
        FROM payments
        WHERE strftime('%Y', date) = ?
        GROUP BY month
        ORDER BY month
    """, (str(year),))
    results = cursor.fetchall()

    monthly_totals = [0.0] * 12
    for month, total in results:
        index = int(month) - 1
        monthly_totals[index] = round(total or 0.0, 2)

    conn.close()
    return monthly_totals

def get_paid_vs_unpaid_counts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            (SELECT COUNT(DISTINCT student_id) FROM payments) AS paid_count,
            (SELECT COUNT(*) FROM students) - 
            (SELECT COUNT(DISTINCT student_id) FROM payments) AS unpaid_count
    """)
    paid, unpaid = cursor.fetchone()
    conn.close()
    return paid, unpaid

def get_monthly_income_multi_years(years):
    conn = create_connection()
    cursor = conn.cursor()
    results = {}

    for year in years:
        cursor.execute("""
            SELECT strftime('%m', date) as month, SUM(amount)
            FROM payments
            WHERE strftime('%Y', date) = ?
            GROUP BY month
        """, (str(year),))
        rows = cursor.fetchall()
        income_by_month = {int(month): amount or 0 for month, amount in rows}
        results[year] = [income_by_month.get(i, 0) for i in range(1, 13)]

    conn.close()
    return results

def get_new_students_monthly_by_years(years):
    conn = create_connection()
    cursor = conn.cursor()
    results = {}

    for year in years:
        monthly_counts = [0] * 12
        cursor.execute("""
            SELECT strftime('%m', registration_date) AS month, COUNT(*) 
            FROM students
            WHERE strftime('%Y', registration_date) = ?
            GROUP BY month
        """, (str(year),))
        for month, count in cursor.fetchall():
            index = int(month) - 1
            monthly_counts[index] = count
        results[year] = monthly_counts

    conn.close()
    return results

def create_expenses_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    

def get_monthly_income_and_expenses_by_year(year):
    conn = create_connection()
    cursor = conn.cursor()

    income = [0] * 12
    expenses = [0] * 12

    cursor.execute("""
        SELECT strftime('%m', date) AS month, SUM(amount)
        FROM payments
        WHERE strftime('%Y', date) = ?
        GROUP BY month
    """, (str(year),))

    for month, total in cursor.fetchall():
        index = int(month) - 1
        income[index] = total or 0

    cursor.execute("""
        SELECT strftime('%m', date) AS month, SUM(amount)
        FROM expenses
        WHERE strftime('%Y', date) = ?
        GROUP BY month
    """, (str(year),))

    for month, total in cursor.fetchall():
        index = int(month) - 1
        expenses[index] = total or 0

    conn.close()
    return income, expenses



def create_subjects_table():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def create_teachers_table():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def create_teacher_subject_table():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS teacher_subject (
            teacher_id INTEGER,
            subject_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)
    conn.commit()
    conn.close()

def create_student_subject_table():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS student_subject (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE (student_id, subject_id)
        )
    """)
    conn.commit()
    conn.close()
    
def get_all_subjects():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return subjects

def get_all_teachers():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, active FROM teachers")
    teachers = cursor.fetchall()
    conn.close()
    return teachers

def add_teacher(name, phone, active):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teachers (name, phone, active)
        VALUES (?, ?, ?)
    """, (name, phone, active))
    teacher_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return teacher_id

def update_teacher(teacher_id, name, phone, active):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teachers
        SET name = ?, phone = ?, active = ?
        WHERE id = ?
    """, (name, phone, active, teacher_id))
    conn.commit()
    conn.close()

def delete_teacher(teacher_id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teacher_subject WHERE teacher_id = ?", (teacher_id,))
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()


def set_teacher_subject(teacher_id, subject_id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teacher_subject WHERE teacher_id = ?", (teacher_id,))
    cursor.execute("""
        INSERT INTO teacher_subject (teacher_id, subject_id)
        VALUES (?, ?)
    """, (teacher_id, subject_id))
    conn.commit()
    conn.close()
def get_teacher_subject(teacher_id, return_id=False):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subjects.id, subjects.name FROM teacher_subject
        JOIN subjects ON teacher_subject.subject_id = subjects.id
        WHERE teacher_subject.teacher_id = ?
    """, (teacher_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        subject_id, subject_name = result
        return subject_id if return_id else subject_name
    return None

def set_student_subjects(student_id, subject_ids):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_subject WHERE student_id = ?", (student_id,))
    for sid in subject_ids:
        cursor.execute("INSERT INTO student_subject (student_id, subject_id) VALUES (?, ?)", (student_id, sid))

    conn.commit()
    conn.close()


def get_student_subjects(student_id):
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        SELECT subjects.id, subjects.name 
        FROM subjects
        INNER JOIN student_subject ON subjects.id = student_subject.subject_id
        WHERE student_subject.student_id = ?
    """, (student_id,))
    subjects = c.fetchall()
    conn.close()
    return subjects 

def get_subjects_for_student(student_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.name
        FROM student_subject ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.student_id = ?
    ''', (student_id,))
    result = cursor.fetchall()
    conn.close()
    return [r[0] for r in result]

def archive_student(student_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET archived = 1 WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

def unarchive_student(student_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET archived = 0 WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

def get_students_for_subject(subject_id):
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        SELECT s.* FROM students s
        JOIN student_subject ss ON s.id = ss.student_id
        WHERE ss.subject_id = ? AND s.archived = 0
    """, (subject_id,))
    students = c.fetchall()
    conn.close()
    return students
def get_teacher_for_subject(subject_id):
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("""
        SELECT t.name FROM teachers t
        JOIN teacher_subject ts ON t.id = ts.teacher_id
        WHERE ts.subject_id = ?
    """, (subject_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "غير معروف"

def get_students_by_subject(subject_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*
        FROM students s
        JOIN student_subject ss ON s.id = ss.student_id
        WHERE ss.subject_id = ? AND s.archived = 0
    ''', (subject_id,))
    students = cursor.fetchall()
    conn.close()
    return students
