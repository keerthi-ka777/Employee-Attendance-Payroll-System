# Employee Attendance & Payroll Management System

A web-based Employee Attendance and Payroll Management System developed using Python Flask and SQLite.

## Project Overview

This system helps manage employee information, attendance records, and monthly payroll calculations through a simple web interface.

## Features

- Add new employees
- View employee details
- Edit employee information
- Delete employees
- Mark employee attendance
- Track Present, Absent, and Leave status
- View attendance records
- Calculate monthly payroll
- Calculate overtime
- View payroll records
- Dashboard showing employee and attendance statistics

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- SQL

## Project Structure

```text
Employee-Attendance-Payroll-System/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
│
├── database/
│   └── employee_payroll.sql
│
├── static/
│   ├── script.js
│   └── style.css
│
└── templates/
    ├── add_employee.html
    ├── attendance.html
    ├── edit_employee.html
    ├── employees.html
    ├── index.html
    └── payroll.html
