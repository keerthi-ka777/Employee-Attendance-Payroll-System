from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, initialize_database
from datetime import date


app = Flask(__name__)

app.secret_key = "employee-payroll-system"

# Create database and tables automatically
initialize_database()


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def index():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    today = date.today().isoformat()

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
    """, (today,))

    present_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Absent'
    """, (today,))

    absent_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Leave'
    """, (today,))

    leave_today = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        leave_today=leave_today
    )


# =====================================================
# EMPLOYEES
# =====================================================

@app.route("/employees")
def employees():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY employee_id DESC
    """)

    employee_list = cursor.fetchall()

    connection.close()

    return render_template(
        "employees.html",
        employees=employee_list
    )


# =====================================================
# ADD EMPLOYEE
# =====================================================

@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        designation = request.form["designation"]
        joining_date = request.form["joining_date"]
        basic_salary = request.form["basic_salary"]

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO employees
                (
                    name,
                    email,
                    department,
                    designation,
                    joining_date,
                    basic_salary
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                department,
                designation,
                joining_date,
                basic_salary
            ))

            connection.commit()

            flash(
                "Employee added successfully!",
                "success"
            )

        except Exception as error:

            connection.rollback()

            flash(
                "Error: " + str(error),
                "danger"
            )

        finally:

            connection.close()

        return redirect(url_for("employees"))

    return render_template("add_employee.html")

# =====================================================
# EDIT EMPLOYEE
# =====================================================

@app.route("/edit-employee/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        designation = request.form["designation"]
        joining_date = request.form["joining_date"]
        basic_salary = request.form["basic_salary"]

        try:

            cursor.execute("""
                UPDATE employees

                SET
                    name = ?,
                    email = ?,
                    department = ?,
                    designation = ?,
                    joining_date = ?,
                    basic_salary = ?

                WHERE employee_id = ?

            """, (
                name,
                email,
                department,
                designation,
                joining_date,
                basic_salary,
                employee_id
            ))

            connection.commit()

            flash(
                "Employee updated successfully!",
                "success"
            )

        except Exception as error:

            connection.rollback()

            flash(
                "Error: " + str(error),
                "danger"
            )

        finally:

            connection.close()

        return redirect(url_for("employees"))

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    employee = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )
# =====================================================
# DELETE EMPLOYEE
# =====================================================

@app.route("/delete-employee/<int:employee_id>")
def delete_employee(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    connection.commit()
    connection.close()

    flash(
        "Employee deleted successfully!",
        "success"
    )

    return redirect(url_for("employees"))


# =====================================================
# ATTENDANCE
# =====================================================

@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        employee_id = request.form["employee_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        try:

            cursor.execute("""
                INSERT INTO attendance
                (
                    employee_id,
                    attendance_date,
                    status
                )
                VALUES (?, ?, ?)
            """, (
                employee_id,
                attendance_date,
                status
            ))

            connection.commit()

            flash(
                "Attendance recorded successfully!",
                "success"
            )

        except Exception:

            connection.rollback()

            flash(
                "Attendance already exists for this employee and date.",
                "danger"
            )

    cursor.execute("""
        SELECT
            a.attendance_id,
            e.name,
            a.attendance_date,
            a.status
        FROM attendance a
        JOIN employees e
        ON a.employee_id = e.employee_id
        ORDER BY a.attendance_date DESC
    """)

    attendance_records = cursor.fetchall()

    cursor.execute("""
        SELECT
            employee_id,
            name
        FROM employees
        ORDER BY name
    """)

    employee_list = cursor.fetchall()

    connection.close()

    return render_template(
        "attendance.html",
        attendance=attendance_records,
        employees=employee_list
    )


# =====================================================
# PAYROLL
# =====================================================

@app.route("/payroll", methods=["GET", "POST"])
def payroll():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        employee_id = request.form["employee_id"]
        month = int(request.form["month"])
        year = int(request.form["year"])
        working_days = int(request.form["working_days"])
        overtime_hours = float(request.form["overtime_hours"])

        cursor.execute("""
            SELECT basic_salary
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if employee:

            basic_salary = float(employee["basic_salary"])

            cursor.execute("""
                SELECT

                    SUM(
                        CASE
                            WHEN status = 'Present'
                            THEN 1 ELSE 0
                        END
                    ) AS present_days,

                    SUM(
                        CASE
                            WHEN status = 'Absent'
                            THEN 1 ELSE 0
                        END
                    ) AS absent_days,

                    SUM(
                        CASE
                            WHEN status = 'Leave'
                            THEN 1 ELSE 0
                        END
                    ) AS leave_days

                FROM attendance

                WHERE employee_id = ?

                AND CAST(
                    strftime('%m', attendance_date)
                    AS INTEGER
                ) = ?

                AND CAST(
                    strftime('%Y', attendance_date)
                    AS INTEGER
                ) = ?

            """, (
                employee_id,
                month,
                year
            ))

            attendance_data = cursor.fetchone()

            present_days = (
                attendance_data["present_days"] or 0
            )

            absent_days = (
                attendance_data["absent_days"] or 0
            )

            leave_days = (
                attendance_data["leave_days"] or 0
            )

            # Salary calculation

            daily_salary = (
                basic_salary / working_days
            )

            deduction = (
                daily_salary * absent_days
            )

            overtime_rate = (
                daily_salary / 8
            )

            overtime_pay = (
                overtime_hours * overtime_rate
            )

            net_salary = (
                basic_salary
                - deduction
                + overtime_pay
            )

            cursor.execute("""
                INSERT INTO payroll
                (
                    employee_id,
                    month,
                    year,
                    working_days,
                    present_days,
                    absent_days,
                    leave_days,
                    overtime_hours,
                    net_salary
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (
                employee_id,
                month,
                year,
                working_days,
                present_days,
                absent_days,
                leave_days,
                overtime_hours,
                net_salary
            ))

            connection.commit()

            flash(
                "Payroll calculated successfully!",
                "success"
            )

    cursor.execute("""
        SELECT

            p.payroll_id,
            e.name,
            p.month,
            p.year,
            p.working_days,
            p.present_days,
            p.absent_days,
            p.leave_days,
            p.overtime_hours,
            p.net_salary

        FROM payroll p

        JOIN employees e
        ON p.employee_id = e.employee_id

        ORDER BY
            p.year DESC,
            p.month DESC
    """)

    payroll_records = cursor.fetchall()

    cursor.execute("""
        SELECT
            employee_id,
            name
        FROM employees
        ORDER BY name
    """)

    employee_list = cursor.fetchall()

    connection.close()

    return render_template(
        "payroll.html",
        payroll=payroll_records,
        employees=employee_list
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)