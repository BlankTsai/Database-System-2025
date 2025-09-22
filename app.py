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

@app.route('/', methods=['GET', 'POST'])
def show_employees():
    employees = []
    if request.method == 'POST':
        # 新增員工
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        
        # 獲取當前時間並格式化
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO employees (name, position, department, created_at) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, position, department, created_at))
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
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching employees: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return render_template('employees.html', employees=employees)

@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
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

if __name__ == '__main__':
    app.run(debug=True)