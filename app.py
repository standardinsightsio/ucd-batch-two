from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    print("File upload route accessed!")  # Debug log
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return jsonify({"error": "No selected file"}), 400

    # Save file with a unique name
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{request.form['upload_type']}_{timestamp}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Log metadata
    log_entry = {
        "filename": filename,
        "upload_type": request.form['upload_type'],
        "timestamp": timestamp
    }
    print(f"File metadata: {log_entry}")

    return jsonify({"message": "File uploaded successfully!", "file": filename}), 200

app.run(debug=True)
