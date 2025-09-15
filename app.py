from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection configuration
# 請替換成你的 MySQL 憑證
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'blank90658',
    'database': 'employeesystem'
}

@app.route('/', methods=['GET', 'POST'])
def show_employees():
    employees = []
    if request.method == 'POST':
        # 處理新增員工的請求
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        salary = request.form['salary']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO employees (name, position, department, salary) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, position, department, salary))
            conn.commit()
            return redirect(url_for('show_employees')) # 新增成功後重定向回首頁
        except mysql.connector.Error as err:
            print(f"Error adding employee: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # 處理 GET 請求，顯示員工列表
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

if __name__ == '__main__':
    app.run(debug=True)