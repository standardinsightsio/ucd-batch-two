from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
from clean_script import clean_uploaded_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        subprocess.run(["python", "filter_script.py", cleaned_file_path], check=True)

        # **Step three**
        filtered_file_path = f"filtered_data/{os.path.basename(cleaned_file_path).replace('cleaned_', '').replace('.csv', '')}_filtered.csv"
        subprocess.run(["python", "loadsql_script.py", filtered_file_path], check=True)
        print(f"Successfully loaded in database {filtered_file_path}")

        return jsonify({"message": "File processed and uploaded successfully!"}), 200
    except Exception as e:
        print(f"Fail to g through process {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)


