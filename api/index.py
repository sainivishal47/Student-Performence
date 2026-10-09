import io
import json
from flask import Flask, render_template_string, request, redirect, url_for, send_file
import pandas as pd

app = Flask(__name__)

DEFAULT_SUBJECTS = [
    {"name": "English", "maximum": 100.0},
    {"name": "Mathematics", "maximum": 100.0},
    {"name": "Science", "maximum": 100.0},
    {"name": "Computer", "maximum": 100.0},
    {"name": "Hindi", "maximum": 100.0},
]

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

        {% if active_tab == 'subjects' %}
            <h2>Manage Subjects</h2>
            <table>
                <tr><th>Subject</th><th>Maximum Marks</th></tr>
                <tbody id="subjectTableBody"></tbody>
            </table>
            
            <h3 style="margin-top:25px;">Add New Subject</h3>
            <form id="addSubjectForm" onsubmit="addSubject(event)">
                <div class="form-group">
                    <label>Subject Name</label>
                    <input type="text" id="subName" required>
                </div>
                <div class="form-group">
                    <label>Maximum Marks</label>
                    <input type="number" id="subMax" value="100" step="1" required>
                </div>
                <button type="submit">Add Subject</button>
            </form>

            <h3 style="margin-top:30px;">Remove a Subject</h3>
            <form id="removeSubjectForm" onsubmit="removeSubject(event)">
                <div class="form-group">
                    <label>Select Subject to Remove</label>
                    <select id="removeSubSelect"></select>
                </div>
                <button type="submit" class="btn-danger">Remove Subject</button>
            </form>

        {% elif active_tab == 'marks' %}
            <h2>Enter Student Marks</h2>
            <form id="saveMarksForm" onsubmit="saveMarks(event)">
                <div class="form-group">
                    <label>Student Full Name</label>
                    <input type="text" id="studentName" required>
                </div>
                <div class="form-group">
                    <label>Roll Number</label>
                    <input type="text" id="rollNumber" required>
                </div>
                <div class="form-group">
                    <label>Class / Section</label>
                    <input type="text" id="className" required>
                </div>
                <h3>Subject-wise Marks</h3>
                <div id="dynamicMarksInputs"></div>
                <button type="submit" style="margin-top:15px;">Calculate and Save Result</button>
            </form>

        {% elif active_tab == 'records' %}
            <h2>Saved Student Results</h2>
            <div id="recordsContainer" style="overflow-x:auto;"></div>
            <br>
            <div id="downloadButtons" style="display:none; gap:10px;">
                <button onclick="downloadCSV()" class="btn">Download CSV</button>
                <button onclick="downloadExcel()" class="btn">Download Excel</button>
            </div>
        {% endif %}

        <div class="footer">
            Created by Vishal Saini
        </div>
    </div>

    <script>
        const DEFAULT_SUBJECTS = [
            {name: "English", maximum: 100.0},
            {name: "Mathematics", maximum: 100.0},
            {name: "Science", maximum: 100.0},
            {name: "Computer", maximum: 100.0},
            {name: "Hindi", maximum: 100.0}
        ];

        function getSubjects() {
            let data = localStorage.getItem("edutrack_subjects");
            if (!data) {
                localStorage.setItem("edutrack_subjects", JSON.stringify(DEFAULT_SUBJECTS));
                return DEFAULT_SUBJECTS;
            }
            return JSON.parse(data);
        }

        function saveSubjectsList(subjects) {
            localStorage.setItem("edutrack_subjects", JSON.stringify(subjects));
        }

        function getResults() {
            let data = localStorage.getItem("edutrack_results");
            return data ? JSON.parse(data) : [];
        }

        function saveResultsList(results) {
            localStorage.setItem("edutrack_results", JSON.stringify(results));
        }

        const tab = "{{ active_tab }}";

        if (tab === "subjects") {
            renderSubjects();
        } else if (tab === "marks") {
            renderMarksForm();
        } else if (tab === "records") {
            renderRecords();
        }

        function renderSubjects() {
            let subjects = getSubjects();
            let tbody = document.getElementById("subjectTableBody");
            let select = document.getElementById("removeSubSelect");
            tbody.innerHTML = "";
            select.innerHTML = "";
            
            subjects.forEach(s => {
                tbody.innerHTML += `<tr><td>${s.name}</td><td>${s.maximum}</td></tr>`;
                select.innerHTML += `<option value="${s.name}">${s.name}</option>`;
            });
        }

        function addSubject(e) {
            e.preventDefault();
            let name = document.getElementById("subName").value.trim();
            let maximum = parseFloat(document.getElementById("subMax").value);
            if (!name) return;

            let subjects = getSubjects();
            if (!subjects.some(s => s.name.toLowerCase() === name.toLowerCase())) {
                subjects.push({name, maximum});
                saveSubjectsList(subjects);
            }
            document.getElementById("subName").value = "";
            renderSubjects();
        }

        function removeSubject(e) {
            e.preventDefault();
            let nameToRemove = document.getElementById("removeSubSelect").value;
            let subjects = getSubjects();
            if (subjects.length > 1) {
                subjects = subjects.filter(s => s.name !== nameToRemove);
                saveSubjectsList(subjects);
                renderSubjects();
            } else {
                alert("At least one subject must remain.");
            }
        }

        function renderMarksForm() {
            let subjects = getSubjects();
            let container = document.getElementById("dynamicMarksInputs");
            container.innerHTML = "";
            subjects.forEach(s => {
                container.innerHTML += `
                    <div class="form-group">
                        <label>${s.name} (Max: ${s.maximum})</label>
                        <input type="number" id="mark_${s.name}" min="0" max="${s.maximum}" step="1" value="0" required>
                    </div>
                `;
            });
        }

        function saveMarks(e) {
            e.preventDefault();
            let name = document.getElementById("studentName").value.trim();
            let roll = document.getElementById("rollNumber").value.trim();
            let className = document.getElementById("className").value.trim();
            let subjects = getSubjects();

            let record = {
                "Student Name": name,
                "Roll Number": roll,
                "Class": className
            };

            let totalObtained = 0;
            let totalMaximum = 0;

            subjects.forEach(s => {
                let val = parseFloat(document.getElementById(`mark_${s.name}`).value) || 0;
                let maxVal = s.maximum;
                record[`${s.name} Obtained`] = val;
                record[`${s.name} Maximum`] = maxVal;
                record[`${s.name} Percentage`] = maxVal > 0 ? parseFloat(((val / maxVal) * 100).toFixed(2)) : 0;
                totalObtained += val;
                totalMaximum += maxVal;
            });

            record["Total Obtained"] = parseFloat(totalObtained.toFixed(2));
            record["Total Maximum"] = parseFloat(totalMaximum.toFixed(2));
            record["Overall Percentage"] = totalMaximum > 0 ? parseFloat(((totalObtained / totalMaximum) * 100).toFixed(2)) : 0;

            let results = getResults();
            results.push(record);
            saveResultsList(results);

            window.location.href = "/records";
        }

        function renderRecords() {
            let results = getResults();
            let container = document.getElementById("recordsContainer");
            let btnContainer = document.getElementById("downloadButtons");

            if (results.length === 0) {
                container.innerHTML = "<p>No student results have been saved yet.</p>";
                btnContainer.style.display = "none";
                return;
            }

            let html = `<table><tr>`;
            let keys = Object.keys(results[0]);
            keys.forEach(k => html += `<th>${k}</th>`);
            html += `</tr>`;

            results.forEach(r => {
                html += `<tr>`;
                keys.forEach(k => html += `<td>${r[k]}</td>`);
                html += `</tr>`;
            });
            html += `</table>`;

            container.innerHTML = html;
            btnContainer.style.display = "flex";
        }

        function downloadCSV() {
            let results = getResults();
            if (results.length === 0) return;
            let keys = Object.keys(results[0]);
            let csvContent = keys.join(",") + "\\n";
            results.forEach(r => {
                let row = keys.map(k => `"${r[k]}"`).join(",");
                csvContent += row + "\\n";
            });

            let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            let url = URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = "student_results.csv";
            a.click();
        }

        function downloadExcel() {
            // Fallback CSV download formatted as .xls for simple client-side browser export
            downloadCSV();
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, active_tab="subjects")

@app.route("/marks")
def marks_page():
    return render_template_string(HTML_TEMPLATE, active_tab="marks")

@app.route("/records")
def records_page():
    return render_template_string(HTML_TEMPLATE, active_tab="records")
