import os
import json
import io
from pathlib import Path
import pandas as pd
from flask import Flask, render_template_string, request, redirect, url_for, send_file

app = Flask(__name__)

BASE_DIR = Path("/tmp")
SUBJECT_FILE = BASE_DIR / "subjects.json"
RESULT_FILE = BASE_DIR / "student_results.csv"

DEFAULT_SUBJECTS = [
    {"name": "English", "maximum": 100.0},
    {"name": "Mathematics", "maximum": 100.0},
    {"name": "Science", "maximum": 100.0},
    {"name": "Computer", "maximum": 100.0},
    {"name": "Hindi", "maximum": 100.0},
]

def validate_subjects(subjects):
    if not isinstance(subjects, list):
        raise ValueError("Subject configuration must be a list.")
    names = set()
    cleaned = []
    for item in subjects:
        if not isinstance(item, dict):
            raise ValueError("Invalid subject record.")
        name = str(item.get("name", "")).strip()
        maximum = float(item.get("maximum", 0))
        if not name:
            raise ValueError("Subject name cannot be empty.")
        if name.casefold() in names:
            raise ValueError(f"Duplicate subject: {name}")
        names.add(name.casefold())
        cleaned.append({"name": name, "maximum": maximum})
    return cleaned if cleaned else DEFAULT_SUBJECTS.copy()

def load_subjects():
    if not SUBJECT_FILE.exists():
        save_subjects(DEFAULT_SUBJECTS)
        return DEFAULT_SUBJECTS.copy()
    try:
        with SUBJECT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return validate_subjects(data)
    except Exception:
        return DEFAULT_SUBJECTS.copy()

def save_subjects(subjects):
    cleaned = validate_subjects(subjects)
    with SUBJECT_FILE.open("w", encoding="utf-8") as file:
        json.dump(cleaned, file, indent=2, ensure_ascii=False)

def load_results():
    if not RESULT_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(RESULT_FILE)
    except Exception:
        return pd.DataFrame()

def save_result(record):
    old_results = load_results()
    new_row = pd.DataFrame([record])
    updated = pd.concat([old_results, new_row], ignore_index=True)
    updated.to_csv(RESULT_FILE, index=False, encoding="utf-8-sig")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Marks Management System</title>
    <style>
        :root {
            --navy: #07152f;
            --navy2: #0c2450;
            --blue: #2563eb;
            --blue2: #3b82f6;
            --text: #eaf2ff;
        }
        body {
            background: linear-gradient(145deg, #07152f, #0b2450 55%, #102f68);
            color: var(--text);
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            background: #0d2245;
            padding: 30px;
            border-radius: 16px;
            border: 1px solid #294773;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        h1, h2, h3 { color: #ffffff; }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #294773;
            padding-bottom: 10px;
        }
        .nav-tabs a {
            background: #102b55;
            color: #dbe8ff;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }
        .nav-tabs a.active {
            background: var(--blue);
            color: white;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label { display: block; margin-bottom: 5px; color: #b9ccec; }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 10px;
            background: #112c56;
            border: 1px solid #40689e;
            border-radius: 8px;
            color: #ffffff;
            box-sizing: border-box;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus {
            border-color: #3b82f6;
            outline: none;
        }
        button, .btn {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        button:hover, .btn:hover { background: #4f91ff; }
        .btn-danger {
            background: linear-gradient(135deg, #ef4444, #b91c1c);
        }
        .btn-danger:hover { background: #f87171; }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #112c56;
            color: #eaf2ff;
            border-radius: 8px;
            overflow: hidden;
            margin-top: 15px;
            border: 1px solid #294773;
        }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #294773; }
        th { background: #0c2450; color: #ffffff; }
        .alert { padding: 10px; background: #1e3b68; border-radius: 8px; margin-bottom: 15px; color: #dbe8ff; }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #294773;
            color: #93c5fd;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="background: linear-gradient(120deg, #101b35, #315efb); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <h1 style="margin:0;">🎓 EduTrack</h1>
            <p style="margin:5px 0 0 0; color:#dbe8ff;">Student Marks, Academic Results & Performance Management</p>
        </div>

        <div class="nav-tabs">
            <a href="/" class="{{ 'active' if active_tab == 'subjects' else '' }}">Manage Subjects</a>
            <a href="/marks" class="{{ 'active' if active_tab == 'marks' else '' }}">Enter Marks</a>
            <a href="/records" class="{{ 'active' if active_tab == 'records' else '' }}">Saved Results</a>
        </div>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="alert">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}

        {% if active_tab == 'subjects' %}
            <h2>Manage Subjects</h2>
            <table>
                <tr><th>Subject</th><th>Maximum Marks</th></tr>
                {% for s in subjects %}
                <tr><td>{{ s.name }}</td><td>{{ s.maximum }}</td></tr>
                {% endfor %}
            </table>
            
            <h3 style="margin-top:25px;">Add New Subject</h3>
            <form method="POST" action="/add_subject">
                <div class="form-group">
                    <label>Subject Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Maximum Marks</label>
                    <input type="number" name="maximum" value="100" step="1" required>
                </div>
                <button type="submit">Add Subject</button>
            </form>

            <h3 style="margin-top:30px;">Remove a Subject</h3>
            <form method="POST" action="/remove_subject">
                <div class="form-group">
                    <label>Select Subject to Remove</label>
                    <select name="subject_name">
                        {% for s in subjects %}
                        <option value="{{ s.name }}">{{ s.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn-danger">Remove Subject</button>
            </form>

        {% elif active_tab == 'marks' %}
            <h2>Enter Student Marks</h2>
            <form method="POST" action="/save_marks">
                <div class="form-group">
                    <label>Student Full Name</label>
                    <input type="text" name="student_name" required>
                </div>
                <div class="form-group">
                    <label>Roll Number</label>
                    <input type="text" name="roll_number" required>
                </div>
                <div class="form-group">
                    <label>Class / Section</label>
                    <input type="text" name="class_name" required>
                </div>
                <h3>Subject-wise Marks</h3>
                {% for s in subjects %}
                <div class="form-group">
                    <label>{{ s.name }} (Max: {{ s.maximum }})</label>
                    <input type="number" name="mark_{{ s.name }}" min="0" max="{{ s.maximum }}" step="1" value="0" required>
                </div>
                {% endfor %}
                <button type="submit">Calculate and Save Result</button>
            </form>

        {% elif active_tab == 'records' %}
            <h2>Saved Student Results</h2>
            {% if saved_html %}
                <div style="overflow-x:auto;">{{ saved_html | safe }}</div>
                <br>
                <a href="/download/csv" class="btn">Download CSV</a>
                <a href="/download/excel" class="btn">Download Excel</a>
            {% else %}
                <p>No student results have been saved yet.</p>
            {% endif %}
        {% endif %}

        <div class="footer">
            Created by Vishal Saini
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    subjects = load_subjects()
    return render_template_string(HTML_TEMPLATE, active_tab="subjects", subjects=subjects)

@app.route("/marks")
def marks_page():
    subjects = load_subjects()
    return render_template_string(HTML_TEMPLATE, active_tab="marks", subjects=subjects)

@app.route("/records")
def records_page():
    saved = load_results()
    saved_html = saved.to_html(classes="dataframe", index=False) if not saved.empty else None
    return render_template_string(HTML_TEMPLATE, active_tab="records", saved_html=saved_html)

@app.route("/add_subject", methods=["POST"])
def add_subject():
    name = request.form.get("name", "").strip()
    try:
        maximum = float(request.form.get("maximum", 100))
        subjects = load_subjects()
        if any(s["name"].casefold() == name.casefold() for s in subjects):
            return redirect(url_for('index'))
        subjects.append({"name": name, "maximum": maximum})
        save_subjects(subjects)
    except Exception:
        pass
    return redirect(url_for('index'))

@app.route("/remove_subject", methods=["POST"])
def remove_subject():
    name_to_remove = request.form.get("subject_name", "").strip()
    subjects = load_subjects()
    if len(subjects) > 1:
        updated = [s for s in subjects if s["name"] != name_to_remove]
        try:
            save_subjects(updated)
        except Exception:
            pass
    return redirect(url_for('index'))

@app.route("/save_marks", methods=["POST"])
def save_marks():
    name = request.form.get("student_name", "").strip()
    roll = request.form.get("roll_number", "").strip()
    class_value = request.form.get("class_name", "").strip()
    
    subjects = load_subjects()
    total_obtained = 0
    total_maximum = 0
    
    record = {
        "Student Name": name,
        "Roll Number": roll,
        "Class": class_value,
    }
    
    for s in subjects:
        val = float(request.form.get(f"mark_{s['name']}", 0))
        max_val = s["maximum"]
        record[f"{s['name']} Obtained"] = val
        record[f"{s['name']} Maximum"] = max_val
        record[f"{s['name']} Percentage"] = round((val / max_val) * 100, 2) if max_val > 0 else 0
        total_obtained += val
        total_maximum += max_val

    record["Total Obtained"] = round(total_obtained, 2)
    record["Total Maximum"] = round(total_maximum, 2)
    record["Overall Percentage"] = round((total_obtained / total_maximum) * 100, 2) if total_maximum > 0 else 0

    save_result(record)
    return redirect(url_for('records_page'))

@app.route("/download/csv")
def download_csv():
    saved = load_results()
    output = io.BytesIO()
    output.write(saved.to_csv(index=False).encode("utf-8-sig"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="student_results.csv")

@app.route("/download/excel")
def download_excel():
    saved = load_results()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        saved.to_excel(writer, index=False, sheet_name="Student Results")
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="student_results.xlsx")
