from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os


app = FastAPI(title="Employee Leave Management System")


# =====================================================
# CORS CONFIGURATION
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# MYSQL CONNECTION
# =====================================================

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "employee_leave_db")
    )


# =====================================================
# DEPARTMENT MODEL
# =====================================================

class Department(BaseModel):

    department_name: str


# =====================================================
# EMPLOYEE MODEL
# =====================================================

class Employee(BaseModel):

    employee_name: str
    email: str
    phone: str
    designation: str
    department_id: int
    joining_date: str


# =====================================================
# LEAVE MODEL
# =====================================================

class Leave(BaseModel):

    employee_id: int
    leave_type: str
    from_date: str
    to_date: str
    reason: str


# =====================================================
# HOME API
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Employee Leave Management API is running"
    }


# =====================================================
# TEST DATABASE
# =====================================================

@app.get("/test-db")
def test_database():

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("SELECT DATABASE()")

        database = cursor.fetchone()

        cursor.close()
        connection.close()

        return {
            "message": "MySQL connection successful",
            "database": database[0]
        }

    except Exception as e:

        return {
            "message": "MySQL connection failed",
            "error": str(e)
        }


# =====================================================
# ADD DEPARTMENT
# =====================================================

@app.post("/departments")
def add_department(department: Department):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO departments
        (department_name)
        VALUES (%s)
    """

    cursor.execute(
        query,
        (department.department_name,)
    )

    connection.commit()

    department_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Department added successfully",
        "department_id": department_id
    }


# =====================================================
# GET DEPARTMENTS
# =====================================================

@app.get("/departments")
def get_departments():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        "SELECT * FROM departments"
    )

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return departments


# =====================================================
# ADD EMPLOYEE
# =====================================================

@app.post("/employees")
def add_employee(employee: Employee):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO employees
        (
            employee_name,
            email,
            phone,
            designation,
            department_id,
            joining_date
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        employee.employee_name,
        employee.email,
        employee.phone,
        employee.designation,
        employee.department_id,
        employee.joining_date
    )

    cursor.execute(query, values)

    connection.commit()

    employee_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Employee added successfully",
        "employee_id": employee_id
    }


# =====================================================
# GET ALL EMPLOYEES
# =====================================================

@app.get("/employees")
def get_employees():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            e.id,
            e.employee_name,
            e.email,
            e.phone,
            e.designation,
            e.department_id,
            d.department_name,
            e.joining_date

        FROM employees e

        LEFT JOIN departments d
        ON e.department_id = d.id
    """

    cursor.execute(query)

    employees = cursor.fetchall()

    cursor.close()
    connection.close()

    return employees


# =====================================================
# UPDATE EMPLOYEE
# =====================================================

@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: Employee
):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        UPDATE employees
        SET
            employee_name = %s,
            email = %s,
            phone = %s,
            designation = %s,
            department_id = %s,
            joining_date = %s

        WHERE id = %s
    """

    values = (
        employee.employee_name,
        employee.email,
        employee.phone,
        employee.designation,
        employee.department_id,
        employee.joining_date,
        employee_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return {
            "message": "Employee not found"
        }

    cursor.close()
    connection.close()

    return {
        "message": "Employee updated successfully"
    }


# =====================================================
# DELETE EMPLOYEE
# =====================================================

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        DELETE FROM employees
        WHERE id = %s
    """

    cursor.execute(
        query,
        (employee_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return {
            "message": "Employee not found"
        }

    cursor.close()
    connection.close()

    return {
        "message": "Employee deleted successfully"
    }


# =====================================================
# APPLY LEAVE
# =====================================================

@app.post("/leaves")
def apply_leave(leave: Leave):

    connection = None
    cursor = None

    try:

        print("====================================")
        print("APPLY LEAVE REQUEST")
        print("Employee ID:", leave.employee_id)
        print("Leave Type:", leave.leave_type)
        print("From Date:", leave.from_date)
        print("To Date:", leave.to_date)
        print("Reason:", leave.reason)
        print("====================================")

        # Connect to MySQL
        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ---------------------------------------------
        # Check Employee Exists
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                employee_name
            FROM employees
            WHERE id = %s
            """,
            (leave.employee_id,)
        )

        employee = cursor.fetchone()

        if employee is None:

            return {
                "message": "Employee ID does not exist"
            }

        # ---------------------------------------------
        # Insert Leave
        # ---------------------------------------------

        query = """
            INSERT INTO leaves
            (
                employee_id,
                leave_type,
                from_date,
                to_date,
                reason,
                status,
                applied_date
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURDATE()
            )
        """

        values = (
            leave.employee_id,
            leave.leave_type,
            leave.from_date,
            leave.to_date,
            leave.reason,
            "Pending"
        )

        cursor.execute(query, values)

        # Get newly created leave ID
        leave_id = cursor.lastrowid

        print(
            "Leave inserted successfully. ID:",
            leave_id
        )

        # ---------------------------------------------
        # CREATE NOTIFICATION
        # ---------------------------------------------

        notification_message = (
            f"New leave request from "
            f"{employee['employee_name']} "
            f"({leave.leave_type})"
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (
                employee_id,
                leave_id,
                message,
                notification_type,
                is_read
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                leave.employee_id,
                leave_id,
                notification_message,
                "Leave",
                False
            )
        )

        print(
            "Notification created successfully."
        )

        # Commit Leave + Notification
        connection.commit()

        return {
            "message": "Leave applied successfully",
            "leave_id": leave_id,
            "status": "Pending",
            "notification": "Notification created successfully"
        }

    except Exception as e:

        # Rollback if database operation failed
        if connection:
            connection.rollback()

        print("====================================")
        print("LEAVE APPLICATION ERROR")
        print(str(e))
        print("====================================")

        return {
            "message": "Leave application failed",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =====================================================
# GET ALL LEAVES
# =====================================================

@app.get("/leaves")
def get_leaves():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            l.id,
            l.employee_id,
            e.employee_name,
            l.leave_type,
            l.from_date,
            l.to_date,
            l.reason,
            l.status,
            l.applied_date

        FROM leaves l

        LEFT JOIN employees e
        ON l.employee_id = e.id

        ORDER BY l.id DESC
    """

    cursor.execute(query)

    leaves = cursor.fetchall()

    cursor.close()
    connection.close()

    return leaves


# =====================================================
# GET NOTIFICATIONS
# =====================================================

@app.get("/notifications")
def get_notifications():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                n.id,
                n.employee_id,
                e.employee_name,
                n.leave_id,
                n.message,
                n.notification_type,
                n.is_read,
                n.created_at

            FROM notifications n

            LEFT JOIN employees e
            ON n.employee_id = e.id

            ORDER BY n.id DESC
        """

        cursor.execute(query)

        notifications = cursor.fetchall()

        return notifications

    except Exception as e:

        print("Notification Error:", e)

        return {
            "message": "Unable to load notifications",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =====================================================
# MARK NOTIFICATION AS READ
# =====================================================

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s
        """

        cursor.execute(
            query,
            (notification_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:

            return {
                "message": "Notification not found"
            }

        return {
            "message": "Notification marked as read"
        }

    except Exception as e:

        if connection:
            connection.rollback()

        return {
            "message": "Unable to update notification",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =====================================================
# APPROVE LEAVE
# =====================================================

@app.put("/leaves/{leave_id}/approve")
def approve_leave(leave_id: int):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ---------------------------------------------
        # Get Leave + Employee
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT
                l.id,
                l.employee_id,
                l.leave_type,
                e.employee_name

            FROM leaves l

            LEFT JOIN employees e
            ON l.employee_id = e.id

            WHERE l.id = %s
            AND l.status = 'Pending'
            """,
            (leave_id,)
        )

        leave_data = cursor.fetchone()

        if leave_data is None:

            return {
                "message":
                    "Leave not found or already processed"
            }

        # ---------------------------------------------
        # Update Leave Status
        # ---------------------------------------------

        cursor.execute(
            """
            UPDATE leaves
            SET status = 'Approved'
            WHERE id = %s
            AND status = 'Pending'
            """,
            (leave_id,)
        )

        # ---------------------------------------------
        # Create Employee Notification
        # ---------------------------------------------

        notification_message = (
            f"Your {leave_data['leave_type']} "
            f"leave request has been approved."
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (
                employee_id,
                leave_id,
                message,
                notification_type,
                is_read
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                leave_data["employee_id"],
                leave_id,
                notification_message,
                "Leave Approval",
                False
            )
        )

        connection.commit()

        return {
            "message": "Leave approved successfully",
            "status": "Approved",
            "notification":
                "Approval notification created"
        }

    except Exception as e:

        if connection:
            connection.rollback()

        print("Approve Leave Error:", e)

        return {
            "message": "Unable to approve leave",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =====================================================
# REJECT LEAVE
# =====================================================

@app.put("/leaves/{leave_id}/reject")
def reject_leave(leave_id: int):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ---------------------------------------------
        # Get Leave + Employee
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT
                l.id,
                l.employee_id,
                l.leave_type,
                e.employee_name

            FROM leaves l

            LEFT JOIN employees e
            ON l.employee_id = e.id

            WHERE l.id = %s
            AND l.status = 'Pending'
            """,
            (leave_id,)
        )

        leave_data = cursor.fetchone()

        if leave_data is None:

            return {
                "message":
                    "Leave not found or already processed"
            }

        # ---------------------------------------------
        # Update Leave Status
        # ---------------------------------------------

        cursor.execute(
            """
            UPDATE leaves
            SET status = 'Rejected'
            WHERE id = %s
            AND status = 'Pending'
            """,
            (leave_id,)
        )

        # ---------------------------------------------
        # Create Employee Notification
        # ---------------------------------------------

        notification_message = (
            f"Your {leave_data['leave_type']} "
            f"leave request has been rejected."
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (
                employee_id,
                leave_id,
                message,
                notification_type,
                is_read
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                leave_data["employee_id"],
                leave_id,
                notification_message,
                "Leave Rejection",
                False
            )
        )

        connection.commit()

        return {
            "message": "Leave rejected successfully",
            "status": "Rejected",
            "notification":
                "Rejection notification created"
        }

    except Exception as e:

        if connection:
            connection.rollback()

        print("Reject Leave Error:", e)

        return {
            "message": "Unable to reject leave",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =====================================================
# REPORTS
# =====================================================

@app.get("/reports")
def get_reports():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # ---------------------------------------------
    # Total Employees
    # ---------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) AS total_employees FROM employees"
    )

    total_employees = cursor.fetchone()


    # ---------------------------------------------
    # Total Leave Requests
    # ---------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) AS total_leaves FROM leaves"
    )

    total_leaves = cursor.fetchone()


    # ---------------------------------------------
    # Pending Leaves
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS pending_leaves
        FROM leaves
        WHERE status = 'Pending'
        """
    )

    pending_leaves = cursor.fetchone()


    # ---------------------------------------------
    # Approved Leaves
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS approved_leaves
        FROM leaves
        WHERE status = 'Approved'
        """
    )

    approved_leaves = cursor.fetchone()


    # ---------------------------------------------
    # Rejected Leaves
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS rejected_leaves
        FROM leaves
        WHERE status = 'Rejected'
        """
    )

    rejected_leaves = cursor.fetchone()


    # ---------------------------------------------
    # Leave Type Summary
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT
            leave_type,
            COUNT(*) AS total

        FROM leaves

        GROUP BY leave_type

        ORDER BY total DESC
        """
    )

    leave_type_summary = cursor.fetchall()


    # ---------------------------------------------
    # Department Employee Count
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT
            d.department_name,
            COUNT(e.id) AS employee_count

        FROM departments d

        LEFT JOIN employees e
        ON d.id = e.department_id

        GROUP BY
            d.id,
            d.department_name

        ORDER BY d.department_name
        """
    )

    department_summary = cursor.fetchall()


    cursor.close()
    connection.close()


    return {

        "total_employees":
            total_employees["total_employees"],

        "total_leaves":
            total_leaves["total_leaves"],

        "pending_leaves":
            pending_leaves["pending_leaves"],

        "approved_leaves":
            approved_leaves["approved_leaves"],

        "rejected_leaves":
            rejected_leaves["rejected_leaves"],

        "leave_type_summary":
            leave_type_summary,

        "department_summary":
            department_summary
    }