import sqlite3

DATABASE = "employee_payroll.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            basic_salary REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent', 'Leave')),
            UNIQUE(employee_id, attendance_date),
            FOREIGN KEY(employee_id)
                REFERENCES employees(employee_id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_date TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(employee_id)
                REFERENCES employees(employee_id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            working_days INTEGER NOT NULL,
            present_days INTEGER NOT NULL,
            absent_days INTEGER NOT NULL,
            leave_days INTEGER NOT NULL,
            overtime_hours REAL DEFAULT 0,
            net_salary REAL,
            FOREIGN KEY(employee_id)
                REFERENCES employees(employee_id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()