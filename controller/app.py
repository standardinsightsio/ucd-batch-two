from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
from datetime import timedelta
import os
import subprocess
import os
import mysql.connector
from model.database import get_connection, fetch_all, fetch_one, serialize_row

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "realworlddata",
    "port":1001
}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'view')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')
print("Template directory:", TEMPLATE_DIR)
filter_script_path = os.path.join(BASE_DIR, "filter_script.py")
loadsql_path = os.path.join(BASE_DIR,"loadsql_script.py")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# 🟢 Route to render the config.html UI
# 🌐 ROUTES TO EACH HTML PAGE
@app.route('/')
def home():
    return render_template("dashboard.html")
@app.route('/upload')
def upload():
    return render_template("upload.html")
@app.route('/config')
def config():
    return render_template("config.html")
@app.route('/customer-report')
def customer_report():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        rows = fetch_all(cursor, "SELECT * FROM customer")
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/product-report')
def product_report():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        rows = fetch_all(cursor, "SELECT * FROM product")
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/sales-report')
def api_sales_report():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        rows = fetch_all(cursor, "SELECT * FROM sales")
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/customers')
def api_customers():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)

        state_raw = fetch_all(cursor, "SELECT State, COUNT(*) AS count FROM customer GROUP BY State")
        state_labels = [row.get("State", "N/A") for row in state_raw]
        state_data = [row.get("count", 0) for row in state_raw]

        income_raw = fetch_all(cursor, "SELECT IncomeLevel, COUNT(*) AS count FROM customer GROUP BY IncomeLevel")
        income_labels = [row.get("IncomeLevel", "N/A") for row in income_raw]
        income_data = [row.get("count", 0) for row in income_raw]

        # Dummy frequency
        frequency_labels = ['1 purchase', '2–3 purchases', '4+ purchases']
        frequency_data = [25, 45, 30]

        cursor.close()
        conn.close()

        return jsonify({
            "state_labels": state_labels,
            "state_data": state_data,
            "income_labels": income_labels,
            "income_data": income_data,
            "frequency_labels": frequency_labels,
            "frequency_data": frequency_data
        })

    except Exception as e:
        import traceback
        print("❌ /api/customers error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/products')
def api_products():
    try:
        import random
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)

        products = fetch_all(cursor, "SELECT * FROM product")

        top_products = fetch_all(cursor, '''
            SELECT p.ProductName, SUM(s.QuantitySold) AS total_quantity
            FROM sales s
            JOIN product p ON s.ProductId = p.ProductId
            GROUP BY p.ProductName
            ORDER BY total_quantity DESC
            LIMIT 5
        ''')
        top_product_labels = [row.get('ProductName', 'N/A') for row in top_products]
        top_product_data = [row.get('total_quantity', 0) for row in top_products]

        # Dummy Profit Data
        profitable_labels = top_product_labels
        profitable_data = [random.uniform(1000, 5000) for _ in top_product_labels]

        category_raw = fetch_all(cursor, '''
            SELECT p.CategoryId, SUM(s.TotalAmount) AS total_sales
            FROM sales s
            JOIN product p ON s.ProductId = p.ProductId
            GROUP BY p.CategoryId
        ''')
        category_labels = [row.get("CategoryId", "N/A") for row in category_raw]
        category_data = [float(row.get("total_sales", 0)) for row in category_raw]

        cursor.close()
        conn.close()

        return jsonify({
            "products": products,
            "top_product_labels": top_product_labels,
            "top_product_data": top_product_data,
            "profitable_labels": profitable_labels,
            "profitable_data": profitable_data,
            "category_labels": category_labels,
            "category_data": category_data
        })

    except Exception as e:
        import traceback
        print("❌ /api/products error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales')
def api_sales():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        # 1. Raw sales data
        sales_rows = fetch_all(cursor, "SELECT * FROM sales")
        # 2. Channel Distribution
        channel_data_raw = fetch_all(cursor, '''
            SELECT SalesChannel, SUM(TotalAmount) AS total_sales
            FROM sales
            GROUP BY SalesChannel
        ''')
        channel_labels = [row.get("SalesChannel", "N/A") for row in channel_data_raw]
        channel_data = [float(row.get("total_sales", 0)) for row in channel_data_raw]
        # 3. Top Customers by Revenue
        customer_data_raw = fetch_all(cursor, '''
            SELECT c.FirstName AS CustomerName, SUM(s.TotalAmount) AS total_revenue
            FROM sales s
            JOIN customer c ON s.CustomerId = c.CustomerId
            GROUP BY c.FirstName
            ORDER BY total_revenue DESC
            LIMIT 5
        ''')
        top_customer_labels = [row.get("CustomerName","N/A") for row in customer_data_raw]
        top_customer_data = [float(row.get("total_revenue",0)) for row in customer_data_raw]
        sales_rows = [serialize_row(row) for row in sales_rows]
        print("Channel Data:", channel_labels, channel_data)
        cursor.close()
        conn.close()
        return jsonify({
            "sales_records": sales_rows,
            "channel_labels": channel_labels,
            "channel_data": channel_data,
            "top_customer_labels": top_customer_labels,
            "top_customer_data": top_customer_data
        })
    except Exception as e:
        print(f"❌ Sales endpoint failed: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/dashboard-summary')
def dashboard_summary():
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)

        total_sales_row = fetch_one(cursor, "SELECT SUM(TotalAmount) AS total_sales FROM sales")
        print('Total Sales Row:', total_sales_row)
        total_sales = total_sales_row["total_sales"] if total_sales_row and total_sales_row["total_sales"] is not None else 0.0

        total_customers_row = fetch_one(cursor, "SELECT COUNT(CustomerId) AS total_customers FROM sales")
        print('Total Customers Row:', total_customers_row)
        total_customers = total_customers_row["total_customers"] if total_customers_row and total_customers_row["total_customers"] is not None else 0

        top_product_row = fetch_one(cursor, '''
            SELECT p.ProductName, SUM(s.QuantitySold) AS total_quantity
            FROM sales s
            JOIN product p ON s.ProductId = p.ProductId
            GROUP BY p.ProductName
            ORDER BY total_quantity DESC
            LIMIT 1
        ''')
        print('Top Product Row:', top_product_row)
        top_product = top_product_row["ProductName"] if top_product_row and top_product_row["ProductName"] is not None else "N/A"

        top_customer_row = fetch_one(cursor, '''
            SELECT c.FirstName, SUM(s.TotalAmount) AS total_spent
            FROM sales s
            JOIN customer c ON s.CustomerId = c.CustomerId
            GROUP BY c.FirstName
            ORDER BY total_spent DESC
            LIMIT 1
        ''')
        print('Top Customer Row:', top_customer_row)
        top_customer = top_customer_row["FirstName"] if top_customer_row and top_customer_row["FirstName"] is not None else "N/A"

        cursor.close()
        conn.close()

        return jsonify({
            "total_sales": round(total_sales, 2),
            "total_customers": total_customers,
            "top_product": top_product,
            "top_customer": top_customer
        })
    except Exception as e:
        import traceback
        print('Exception in /api/dashboard-summary:', traceback.format_exc())
        return jsonify({"error": str(e)}), 500
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Start receiving")
        if 'file' not in request.files:
            print("No file")
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if file.filename == '':
            print("Empty name")
            return jsonify({"error": "No selected file"}), 400
        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # **Step one*
        cleaned_file_path = clean_uploaded_file(file_path, "cleaned_" + file.filename)
        # **Step two**
        cleaned_file_path = os.path.abspath(cleaned_file_path)
        subprocess.run(["python", filter_script_path, cleaned_file_path], check=True)
        # Construct filtered_file_path with BASE_DIR too:
        filtered_file_path = os.path.join(BASE_DIR, "filtered_data",
            os.path.basename(cleaned_file_path).replace("cleaned_", "").replace(".csv", "") + "_filtered.csv")
        try:
            result = subprocess.run(
                ["python", loadsql_path, filtered_file_path],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"LoadSQL failed: {e.stderr}")
            return jsonify({"error": f"LoadSQL failed: {e.stderr}"}), 500
        print(f"Successfully loaded in database {filtered_file_path}")
        return jsonify({"message": "File processed and uploaded successfully!"}), 200
    except Exception as e:
        print(f"Fail to g through process {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
if __name__ == '__main__':
    app.run(debug=True)