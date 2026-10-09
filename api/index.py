import io
import json
from flask import Flask, render_template_string, request

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
        
        /* Professional Clean A4 Marksheet Styling */
        .marksheet-card {
            background: #ffffff;
            color: #000000;
            width: 210mm;
            min-height: 297mm;
            margin: 20px auto;
            padding: 20mm;
            box-sizing: border-box;
            border-radius: 4px;
            border: 2px solid #000000;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative;
        }
        .marksheet-header {
            text-align: center;
            border-bottom: 3px double #000000;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .marksheet-header h2 { margin: 0; color: #000000; font-size: 24px; font-weight: 800; letter-spacing: 1px; }
        .marksheet-header p { margin: 5px 0 0 0; color: #333333; font-size: 14px; font-weight: 600; }
        
        .student-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            background: #ffffff;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #000000;
            margin-bottom: 20px;
            font-size: 15px;
            color: #000000;
            font-weight: 600;
        }
        
        .marksheet-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .marksheet-table th, .marksheet-table td {
            border: 1px solid #000000;
            padding: 10px;
            text-align: center;
            color: #000000;
            background: #ffffff !important;
        }
        .marksheet-table th {
            background: #f1f5f9 !important;
            color: #000000;
            font-weight: 800;
            border-bottom: 2px solid #000000;
        }
        
        /* Visualization Progress bars */
        .chart-container {
            margin-top: 20px;
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #294773;
            color: #000000;
        }
        .chart-bar-wrap {
            margin-bottom: 12px;
        }
        .chart-label {
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 700;
            color: #eaf2ff;
            margin-bottom: 4px;
        }
        .chart-bar-bg {
            background: #112c56;
            border-radius: 4px;
            height: 14px;
            width: 100%;
            overflow: hidden;
            border: 1px solid #40689e;
        }
        .chart-bar-fill {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            height: 100%;
        }

        .marksheet-footer {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        @media print {
            body { background: none; padding: 0; color: #000; }
            .container > *:not(#recordsContainer) { display: none; }
            .container { background: none; border: none; box-shadow: none; padding: 0; max-width: 100%; }
            .marksheet-card { box-shadow: none; margin: 0; width: 100%; border: 1px solid #000; page-break-after: always; }
            .no-print { display: none !important; }
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #294773;
            color: #93c5fd;
            font-size: 14px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="background: linear-gradient(120deg, #101b35, #315efb); padding: 20px; border-radius: 12px; margin-bottom: 20px;" class="no-print">
            <h1 style="margin:0;">🎓 EduTrack</h1>
            <p style="margin:5px 0 0 0; color:#dbe8ff;">Student Marks, Academic Results & Performance Management</p>
        </div>

        <div class="nav-tabs no-print">
            <a href="/" class="{{ 'active' if active_tab == 'subjects' else '' }}">Manage Subjects</a>
            <a href="/marks" class="{{ 'active' if active_tab == 'marks' else '' }}">Enter Marks</a>
            <a href="/records" class="{{ 'active' if active_tab == 'records' else '' }}">Saved Marksheets</a>
            <a href="/visualization" class="{{ 'active' if active_tab == 'visualization' else '' }}">Visualization</a>
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
                    <label>Class / Semester</label>
                    <input type="text" id="className" required>
                </div>
                <h3>Subject-wise Marks</h3>
                <div id="dynamicMarksInputs"></div>
                <button type="submit" style="margin-top:15px;">Generate Marksheet</button>
            </form>

        {% elif active_tab == 'records' %}
            <div style="display: flex; justify-content: space-between; align-items: center;" class="no-print">
                <h2>Generated Student Marksheets (A4 Format)</h2>
                <div>
                    <button onclick="window.print()" class="btn">🖨️ Print / Save as PDF</button>
                    <button onclick="downloadCSV()" class="btn" style="background: #059669;">📥 Download CSV</button>
                </div>
            </div>
            <div id="recordsContainer"></div>

        {% elif active_tab == 'visualization' %}
            <h2>Student Performance Visualization</h2>
            <div id="visualizationContainer"></div>
        {% endif %}

        <div class="footer no-print">
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
        } else if (tab === "visualization") {
            renderVisualization();
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

            let subjectDetails = [];
            let totalObtained = 0;
            let totalMaximum = 0;

            subjects.forEach(s => {
                let val = parseFloat(document.getElementById(`mark_${s.name}`).value) || 0;
                let maxVal = s.maximum;
                let percentage = maxVal > 0 ? parseFloat(((val / maxVal) * 100).toFixed(2)) : 0;
                
                subjectDetails.push({
                    name: s.name,
                    obtained: val,
                    maximum: maxVal,
                    percentage: percentage
                });

                totalObtained += val;
                totalMaximum += maxVal;
            });

            let overallPercentage = totalMaximum > 0 ? parseFloat(((totalObtained / totalMaximum) * 100).toFixed(2)) : 0;

            let record = {
                "Student Name": name,
                "Roll Number": roll,
                "Class": className,
                "Subjects": subjectDetails,
                "Total Obtained": parseFloat(totalObtained.toFixed(2)),
                "Total Maximum": parseFloat(totalMaximum.toFixed(2)),
                "Overall Percentage": overallPercentage
            };

            let results = getResults();
            results.push(record);
            saveResultsList(results);

            window.location.href = "/records";
        }

        function renderRecords() {
            let results = getResults();
            let container = document.getElementById("recordsContainer");

            if (results.length === 0) {
                container.innerHTML = "<p style='margin-top:20px;'>No student marksheets have been generated yet.</p>";
                return;
            }

            let html = "";
            results.forEach((r, idx) => {
                html += `
                    <div class="marksheet-card">
                        <div class="marksheet-header">
                            <h2>OFFICIAL ACADEMIC PERFORMANCE MARKSHEET</h2>
                            <p>Statement of Marks & Evaluation</p>
                        </div>
                        
                        <div class="student-info-grid">
                            <div><strong>Student Name:</strong> ${r["Student Name"]}</div>
                            <div><strong>Roll Number:</strong> ${r["Roll Number"]}</div>
                            <div><strong>Class / Semester:</strong> ${r["Class"]}</div>
                            <div><strong>Status:</strong> <span style="color: #16a34a; font-weight: bold;">PASSED</span></div>
                        </div>

                        <table class="marksheet-table">
                            <tr>
                                <th>Subject Name</th>
                                <th>Maximum Marks</th>
                                <th>Marks Obtained</th>
                                <th>Percentage</th>
                            </tr>
                `;

                r["Subjects"].forEach(sub => {
                    html += `
                        <tr>
                            <td style="text-align:left; font-weight:600; background:#ffffff;">${sub.name}</td>
                            <td style="background:#ffffff;">${sub.maximum}</td>
                            <td style="background:#ffffff;">${sub.obtained}</td>
                            <td style="background:#ffffff;">${sub.percentage}%</td>
                        </tr>
                    `;
                });

                html += `
                            <tr style="font-weight:bold;">
                                <td style="text-align:left; background:#ffffff;">TOTAL / OVERALL</td>
                                <td style="background:#ffffff;">${r["Total Maximum"]}</td>
                                <td style="background:#ffffff;">${r["Total Obtained"]}</td>
                                <td style="background:#ffffff; color:#000000;">${r["Overall Percentage"]}%</td>
                            </tr>
                        </table>

                        <div class="marksheet-footer">
                            <div>
                                <p style="margin:0; font-size:13px; color:#333;">Date: ${new Date().toLocaleDateString()}</p>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-family: monospace; font-weight:bold; color:#000000; font-size:16px; border-bottom: 2px solid #000000; padding-bottom:5px; width:150px;">Vishal Saini</div>
                                <p style="margin:5px 0 0 0; font-size:12px; color:#333;">Controller of Examination</p>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function renderVisualization() {
            let results = getResults();
            let container = document.getElementById("visualizationContainer");

            if (results.length === 0) {
                container.innerHTML = "<p style='margin-top:20px;'>No student data available for visualization yet.</p>";
                return;
            }

            let html = "";
            results.forEach((r, idx) => {
                html += `
                    <div class="chart-container">
                        <h3 style="margin:0 0 5px 0; color:#ffffff;">${r["Student Name"]} (Roll: ${r["Roll Number"]} | Class: ${r["Class"]})</h3>
                        <p style="margin:0 0 15px 0; color:#93c5fd; font-size:14px;">Overall Percentage: <strong>${r["Overall Percentage"]}%</strong></p>
                `;

                r["Subjects"].forEach(sub => {
                    html += `
                        <div class="chart-bar-wrap">
                            <div class="chart-label">
                                <span>${sub.name}</span>
                                <span>${sub.obtained} / ${sub.maximum} (${sub.percentage}%)</span>
                            </div>
                            <div class="chart-bar-bg">
                                <div class="chart-bar-fill" style="width: ${sub.percentage}%;"></div>
                            </div>
                        </div>
                    `;
                });

                html += `</div><br>`;
            });

            container.innerHTML = html;
        }

        function downloadCSV() {
            let results = getResults();
            if (results.length === 0) return;
            
            let csvContent = "Student Name,Roll Number,Class,Total Obtained,Total Maximum,Overall Percentage\\n";
            results.forEach(r => {
                csvContent += `\\"${r["Student Name"]}\\",\\"${r["Roll Number"]}\\",\\"${r["Class"]}\\",${r["Total Obtained"]},${r["Total Maximum"]},${r["Overall Percentage"]}\\n`;
            });

            let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            let url = URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = "student_results_summary.csv";
            a.click();
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

@app.route("/visualization")
def visualization_page():
    return render_template_string(HTML_TEMPLATE, active_tab="visualization")
