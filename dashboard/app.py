from flask import Flask, jsonify, render_template
import mysql.connector
import pandas as pd
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)

@app.template_filter('format_comma')
def format_comma(value):
    try:
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value
CORS(app)

db_config = {
    "host": "172.233.137.237",
    "user": "sphartiyal",
    "password": "Unbr34k@ble#",
    "database": "realworlddata"
}

def generate_insight(section_title: str, data_dict: dict):
    import json
    import requests

    custom_prompt = data_dict.pop("prompt", None)

    try:
        # Combine section title + custom prompt or fallback
        prompt = custom_prompt or (
            f"You are an expert business analyst. Given the product dashboard data below, identify patterns and summarize key insights and give within 100 words\n\n"
            f"Section: {section_title}\n\n"
            f"{json.dumps(data_dict, indent=2)}\n\n"
            f"DO NOT repeat the raw data or product names. Instead, explain what this data implies —  such as top performers, low profitability, dominant categories, or any surprising trends. Write 2-3 short insights in plain English."
        )
    #add section to customize in app
    #within 100 words

        # OpenAI Chat API endpoint
        OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
        OPENAI_API_KEY = "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"  # 🔐 Replace with your actual key
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4",  # Or "gpt-4-1106-preview" for turbo
            "messages": [
                {"role": "system", "content": "You are a helpful business analyst that summarizes data into actionable insights."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()

        return f"AI response error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Insight generation failed: {str(e)}"

     


# Fetch all tables as DataFrames at app startup
def fetch_data():
    conn = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        auth_plugin='mysql_native_password'
    )

    sales_df = pd.read_sql("SELECT * FROM Sales", conn)
    product_df = pd.read_sql("SELECT * FROM Product", conn)
    customer_df = pd.read_sql("SELECT * FROM Customer", conn)
    category_df = pd.read_sql("SELECT * FROM Category", conn)

    conn.close()
    return sales_df, product_df, customer_df, category_df

sales_df, product_df, customer_df, category_df = fetch_data()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/dashboard-summary')
def dashboard_summary():
    merged = sales_df.merge(product_df, on='ProductId', how='left')
    total_sales = round((merged['QuantitySold'] * merged['Price']).sum(), 2)
    total_customers = customer_df['CustomerId'].nunique()
    
    top_product = merged.groupby('ProductId').agg({'QuantitySold': 'sum'}).sort_values('QuantitySold', ascending=False).head(1)
    top_product_name = product_df.loc[product_df['ProductId'] == top_product.index[0], 'ProductName'].values[0]

    revenue_per_customer = merged.groupby('CustomerId').apply(lambda x: (x['QuantitySold'] * x['Price']).sum())
    top_customer_id = revenue_per_customer.sort_values(ascending=False).index[0]
    top_customer_name = customer_df.loc[customer_df['CustomerId'] == top_customer_id, 'FirstName'].values[0]

    return jsonify({
        "total_sales": total_sales,
        "total_customers": total_customers,
        "top_product": top_product_name,
        "top_customer": top_customer_name
    })

@app.route('/api/sales')
def sales_analysis():
    merged = sales_df.merge(product_df, on='ProductId', how='left')

    sales_df_copy = merged.copy()
    sales_df_copy['Month'] = pd.to_datetime(sales_df_copy['TransactionDate']).dt.strftime('%b')
    monthly_sales = sales_df_copy.groupby('Month').apply(lambda x: (x['QuantitySold'] * x['Price']).sum())

    channel_sales = sales_df_copy.groupby('SalesChannel').apply(lambda x: (x['QuantitySold'] * x['Price']).sum())

    top_customers = sales_df_copy.groupby('CustomerId').apply(lambda x: (x['QuantitySold'] * x['Price']).sum()).sort_values(ascending=False).head(5)
    top_customer_names = customer_df.set_index('CustomerId').loc[top_customers.index]['FirstName'].tolist()

    # Generate insights
    monthly_insight = generate_insight("Monthly Sales Trend", {
        "months": monthly_sales.index.tolist(),
        "sales": monthly_sales.values.tolist()
    })

    monthly_insight_summary = generate_insight("Monthly Sales Trend", {
        "months": monthly_sales.index.tolist(),
        "sales": monthly_sales.values.tolist()
    })

    channel_insight = generate_insight("Sales by Channel", {
        "channels": channel_sales.index.tolist(),
        "sales": channel_sales.values.tolist()
    })

    customer_insight = generate_insight("Top Customer Revenue", {
        "customers": top_customer_names,
        "revenue": top_customers.values.tolist()
    })

    return jsonify({
        "monthly_labels": monthly_sales.index.tolist(),
        "monthly_data": monthly_sales.values.tolist(),
        "channel_labels": channel_sales.index.tolist(),
        "channel_data": channel_sales.values.tolist(),
        "top_customer_labels": top_customer_names,
        "top_customer_data": top_customers.values.tolist(),
        "monthly_insight": monthly_insight,
        "channel_insight": channel_insight,
        "customer_insight": customer_insight,
        "monthly_insight_summary": monthly_insight_summary
    })

@app.route('/api/products')
def products_analysis():
    merged = sales_df.merge(product_df, on='ProductId', how='left')

    top_products = merged.groupby('ProductId')['QuantitySold'].sum().sort_values(ascending=False).head(5)
    top_product_names = product_df.set_index('ProductId').loc[top_products.index]['ProductName'].tolist()

    profit = merged.copy()
    profit['Profit'] = (profit['Price'] - profit['DiscountedPrice']) * profit['QuantitySold']
    top_profit = profit.groupby('ProductId')['Profit'].sum().sort_values(ascending=False).head(5)
    top_profit_names = product_df.set_index('ProductId').loc[top_profit.index]['ProductName'].tolist()

    merged_with_category = merged.merge(category_df, on='CategoryId', how='left')
    category_sales = merged_with_category.groupby('CategoryName').apply(lambda x: (x['QuantitySold'] * x['Price']).sum())

    # Prepare insight data
    insight_data = {
        "top_product_labels": top_product_names,
        "top_product_data": top_products.values.tolist(),
        "profitable_labels": top_profit_names,
        "profitable_data": top_profit.values.tolist(),
        "category_labels": category_sales.index.tolist(),
        "category_data": category_sales.values.tolist()
    }

    # Generate 3 separate insights
    best_selling_insight = generate_insight("Best Selling Products", {
        "product_names": top_product_names,
        "units_sold": top_products.values.tolist()
    })

    best_selling_insight_two = generate_insight("Best Selling Products", {
        "product_names": top_product_names,
        "units_sold": top_products.values.tolist()
    })

    profitable_insight = generate_insight("Most Profitable Products", {
        "product_names": top_profit_names,
        "profits": top_profit.values.tolist()
    })

    category_insight = generate_insight("Sales by Product Category", {
        "categories": category_sales.index.tolist(),
        "sales": category_sales.values.tolist()
    })

    return jsonify({
        **insight_data,
        "best_selling_insight": best_selling_insight,
       "best_selling_insight_two":best_selling_insight_two,
        "profitable_insight": profitable_insight,
        "category_insight": category_insight
    })

@app.route('/api/customers')
def customer_analysis():
    # State distribution
    state_data = customer_df.groupby('State').size()

    # Income level distribution
    income_data = customer_df.groupby('IncomeLevel').size()

    # Purchase frequency bucket creation
    frequency = sales_df.groupby('CustomerId').size()
    buckets = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6+': 0}
    for count in frequency.values:
        if count >= 6:
            buckets['6+'] += 1
        else:
            buckets[str(count)] += 1

    # Convert labels and values
    state_labels = state_data.index.tolist()
    state_counts = state_data.values.tolist()
    income_levels = income_data.index.tolist()
    income_counts = income_data.values.tolist()
    purchase_counts = list(buckets.keys())
    customer_counts = list(buckets.values())

    # Format data for better insight generation
    formatted_state_data = "\n".join([f"{state}: {count}" for state, count in zip(state_labels, state_counts)])
    formatted_income_data = "\n".join([f"{level}: {count}" for level, count in zip(income_levels, income_counts)])
    formatted_frequency_data = "\n".join([f"{bucket} purchases: {count} customers" for bucket, count in zip(purchase_counts, customer_counts)])

    # Insights using formatted prompts
    state_insight = generate_insight("Geographic Customer Distribution", {
        "formatted_data": formatted_state_data,
       
    })

    income_insight = generate_insight("Income-Level Segmentation", {
        "formatted_data": formatted_income_data,
       
    })


    frequency_insight = generate_insight("Customer Purchase Frequency", {
        "formatted_data": formatted_frequency_data,
        

        
    })

    # API response
    return jsonify({
        "state_labels": state_labels,
        "state_data": state_counts,
        "income_labels": income_levels,
        "income_data": income_counts,
        "frequency_labels": purchase_counts,
        "frequency_data": customer_counts,
        "state_insight": state_insight,
        "income_insight": income_insight,
        "frequency_insight": frequency_insight,
        "formatted_data": formatted_frequency_data,
        "formatted_data": formatted_income_data,
        "formatted_data": formatted_state_data
    })
if __name__ == '__main__':
    app.run(debug=True)