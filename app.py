from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'blank940658',
    'database': 'employeesystem'
}

# --- 輔助函數：取得所有部門和職位 ---
# (我們會在很多地方用到，所以獨立出來)
def get_departments_and_positions():
    departments = []
    positions = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM departments")
        departments = cursor.fetchall()
        
        cursor.execute("SELECT * FROM positions")
        positions = cursor.fetchall()
        
    except mysql.connector.Error as err:
        print(f"Error fetching departments/positions: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return departments, positions

# --- 員工 CRUD (修改) ---

@app.route('/', methods=['GET', 'POST'])
def show_employees():
    employees = []
    if request.method == 'POST':
        # 新增員工
        name = request.form['name']
        email = request.form['email']
        # MODIFIED: 儲存 ID 而不是文字
        department_id = request.form['department_id']
        position_id = request.form['position_id']
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # MODIFIED: 插入 ID
            sql = "INSERT INTO employees (name, email, department_id, position_id, created_at) VALUES (%s, %s, %s, %s, %s)"
            # 處理可能為空的 'None' 字串
            dept_id = department_id if department_id else None
            pos_id = position_id if position_id else None
            cursor.execute(sql, (name, email, dept_id, pos_id, created_at))
            conn.commit()
            return redirect(url_for('show_employees'))
        except mysql.connector.Error as err:
            print(f"Error adding employee: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # 顯示員工列表
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # *** REQUIREMENT 3: JOIN ***
        # MODIFIED: 使用 JOIN 查詢
        sql = """
            SELECT 
                e.id, e.name, e.email, e.created_at,
                d.name AS department_name,
                p.title AS position_title,
                e.department_id,
                e.position_id
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            LEFT JOIN positions p ON e.position_id = p.id
            ORDER BY e.id
        """
        cursor.execute(sql)
        employees = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching employees: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
    # MODIFIED: 取得部門和職位列表，傳給前端的 "新增表單"
    departments, positions = get_departments_and_positions()
    return render_template('employees.html', employees=employees, departments=departments, positions=positions)

@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    # (此功能不需變更)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "DELETE FROM employees WHERE id = %s"
        cursor.execute(sql, (employee_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting employee: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('show_employees'))

@app.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = None
    if request.method == 'POST':
        # 修改員工資料
        name = request.form['name']
        email = request.form['email']
        # MODIFIED: 取得 ID
        department_id = request.form['department_id']
        position_id = request.form['position_id']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # MODIFIED: 更新 ID
            sql = "UPDATE employees SET name = %s, email = %s, department_id = %s, position_id = %s WHERE id = %s"
            dept_id = department_id if department_id else None
            pos_id = position_id if position_id else None
            cursor.execute(sql, (name, email, dept_id, pos_id, employee_id))
            conn.commit()
            return redirect(url_for('show_employees'))
        except mysql.connector.Error as err:
            print(f"Error updating employee: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    else:
        # 顯示編輯表單
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            # MODIFIED: 這裡不需要 JOIN，因為我們只需要 ID
            sql = "SELECT * FROM employees WHERE id = %s"
            cursor.execute(sql, (employee_id,))
            employee = cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error fetching employee for edit: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    if employee:
        # MODIFIED: 取得部門和職位列表，傳給前端的 "編輯表單"
        departments, positions = get_departments_and_positions()
        return render_template('edit_employee.html', employee=employee, departments=departments, positions=positions)
    else:
        return redirect(url_for('show_employees'))


# --- NEW: 部門 CRUD (Requirement 2) ---

@app.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    if request.method == 'POST':
        # 新增部門
        name = request.form['name']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO departments (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error adding department: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        return redirect(url_for('manage_departments'))

    # 顯示部門列表
    departments = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM departments")
        departments = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching departments: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/departments/edit/<int:dept_id>', methods=['POST'])
def edit_department(dept_id):
    name = request.form['name']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "UPDATE departments SET name = %s WHERE id = %s"
        cursor.execute(sql, (name, dept_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error updating department: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_departments'))

@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # 注意：因為我們設定了 ON DELETE SET NULL，
        # 刪除部門會讓相關員工的 department_id 變為 NULL
        sql = "DELETE FROM departments WHERE id = %s"
        cursor.execute(sql, (dept_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting department: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_departments'))

# --- NEW: 職位 CRUD (Requirement 2) ---

@app.route('/positions', methods=['GET', 'POST'])
def manage_positions():
    if request.method == 'POST':
        # 新增職位
        title = request.form['title']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO positions (title) VALUES (%s)"
            cursor.execute(sql, (title,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error adding position: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        return redirect(url_for('manage_positions'))

    # 顯示職位列表
    positions = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM positions")
        positions = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching positions: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return render_template('positions.html', positions=positions)

@app.route('/positions/edit/<int:pos_id>', methods=['POST'])
def edit_position(pos_id):
    title = request.form['title']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "UPDATE positions SET title = %s WHERE id = %s"
        cursor.execute(sql, (title, pos_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error updating position: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_positions'))

@app.route('/positions/delete/<int:pos_id>', methods=['POST'])
def delete_position(pos_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # 同樣，刪除職位會讓相關員工的 position_id 變為 NULL
        sql = "DELETE FROM positions WHERE id = %s"
        cursor.execute(sql, (pos_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting position: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_positions'))


if __name__ == '__main__':
    app.run(debug=True)