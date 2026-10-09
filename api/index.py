
from pathlib import Path
import json
import io

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
SUBJECT_FILE = BASE_DIR / "subjects.json"
RESULT_FILE = BASE_DIR / "student_results.csv"

st.set_page_config(
    page_title="Student Marks Management System",
    page_icon="🎓",
    layout="wide"
)


st.markdown("""
<style>
:root {
    --navy: #07152f;
    --navy2: #0c2450;
    --blue: #2563eb;
    --blue2: #3b82f6;
    --line: #294773;
    --text: #eaf2ff;
}

/* Premium dark-blue application */
.stApp {
    background: linear-gradient(145deg, #07152f, #0b2450 55%, #102f68);
    color: #eaf2ff;
    font-family: "Segoe UI", Arial, sans-serif;
}

.block-container {
    max-width: 1500px;
    padding: 2rem 2rem 3rem;
}

/* Professional headings */
h1, h2, h3, h4 {
    color: #ffffff !important;
    font-weight: 750 !important;
    letter-spacing: -0.3px;
}

p, label, [data-testid="stMarkdownContainer"] {
    color: #dbe8ff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #061127;
    border-right: 1px solid #1e3b68;
}

[data-testid="stSidebar"] * {
    color: #eaf2ff;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0b1f42;
    padding: 7px;
    border: 1px solid #24436f;
    border-radius: 13px;
    gap: 7px;
}

.stTabs [data-baseweb="tab"] {
    background: #102b55;
    color: #dbe8ff;
    border-radius: 9px;
    padding: 12px 18px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
}

/* KPI cards and forms */
[data-testid="stMetric"],
[data-testid="stForm"] {
    background: linear-gradient(145deg, #112c56, #0d2245);
    border: 1px solid #294773;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
}

[data-testid="stMetricLabel"] {
    color: #b9ccec !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800;
}

/* Readable input fields */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] {
    background: #f8fbff !important;
    border: 1px solid #aac5f2 !important;
    border-radius: 9px;
}

[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #102448 !important;
    -webkit-text-fill-color: #102448 !important;
}

[data-baseweb="select"] * {
    color: #102448 !important;
}

/* Executive-style blue buttons */
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: #ffffff !important;
    border: 1px solid #6099ff;
    border-radius: 10px;
    min-height: 42px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
    background: #4f91ff;
    border-color: #a8caff;
    box-shadow: 0 5px 18px rgba(37, 99, 235, 0.28);
    transform: translateY(-1px);
}

/* Data tables */
[data-testid="stDataFrame"] {
    background: #ffffff;
    border: 1px solid #cbdaf0;
    border-radius: 12px;
    overflow: hidden;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Separators and captions */
hr {
    border-color: #294773;
}

[data-testid="stCaptionContainer"] {
    color: #b9ccec;
}

/* Responsive layout */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)
# ------------------ SUBJECT STORAGE ------------------

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
        if len(name) > 80:
            raise ValueError("Subject name must be 80 characters or less.")
        if name.casefold() in names:
            raise ValueError(f"Duplicate subject: {name}")
        if not 0 < maximum <= 10000:
            raise ValueError(f"Invalid maximum marks for {name}.")

        names.add(name.casefold())
        cleaned.append({"name": name, "maximum": maximum})

    if not cleaned:
        raise ValueError("At least one subject is required.")

    return cleaned


def load_subjects():
    if not SUBJECT_FILE.exists():
        save_subjects(DEFAULT_SUBJECTS)
        return DEFAULT_SUBJECTS.copy()

    with SUBJECT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return validate_subjects(data)


def save_subjects(subjects):
    cleaned = validate_subjects(subjects)
    temporary_file = SUBJECT_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(cleaned, file, indent=2, ensure_ascii=False)

    temporary_file.replace(SUBJECT_FILE)


# ------------------ RESULT STORAGE ------------------

def load_results():
    if not RESULT_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(RESULT_FILE)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        st.error(
            "Could not read the saved results file. "
            "Back up student_results.csv before repairing it."
        )
        st.stop()


def save_result(record):
    old_results = load_results()
    new_row = pd.DataFrame([record])
    updated = pd.concat([old_results, new_row], ignore_index=True)

    temporary_file = RESULT_FILE.with_suffix(".tmp")
    updated.to_csv(temporary_file, index=False, encoding="utf-8-sig")
    temporary_file.replace(RESULT_FILE)


# ------------------ INITIALIZE APP ------------------

if "subjects" not in st.session_state:
    try:
        st.session_state.subjects = load_subjects()
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        st.error(f"Could not load subjects: {error}")
        st.stop()




st.markdown("""
<div style="
    background: linear-gradient(120deg, #101b35, #315efb);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 24px;
    color: white;
">
    <div style="font-size: 13px; letter-spacing: 2px; opacity: 0.8;">
        EDUCATION MANAGEMENT PLATFORM
    </div>
    <h1 style="color: white !important; margin: 8px 0;">
        🎓 EduTrack
    </h1>
    <p style="font-size: 16px; margin-bottom: 0;">
        Student Marks, Academic Results & Performance Management
    </p>
</div>
""", unsafe_allow_html=True)

tab_subjects, tab_marks, tab_records = st.tabs([
    "Manage Subjects",
    "Enter Student Marks",
    "Saved Results"
])


# ------------------ TAB 1: SUBJECT MANAGEMENT ------------------

with tab_subjects:
    st.header("Manage Subjects")
    st.write(
        "Teacher can add, rename, change maximum marks, "
        "or remove subjects."
    )

    subjects = st.session_state.subjects

    st.dataframe(
        pd.DataFrame(subjects).rename(columns={
            "name": "Subject",
            "maximum": "Maximum Marks"
        }),
        hide_index=True,
        use_container_width=True
    )

    with st.form("add_subject_form", clear_on_submit=True):
        st.subheader("Add New Subject")
        new_name = st.text_input("Subject name")
        new_maximum = st.number_input(
            "Maximum marks",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=1.0
        )
        add_clicked = st.form_submit_button("Add Subject")

    if add_clicked:
        name = new_name.strip()

        if not name:
            st.error("Please enter a subject name.")
        elif any(s["name"].casefold() == name.casefold()
                 for s in subjects):
            st.error("This subject already exists.")
        elif len(name) > 80:
            st.error("Subject name must be 80 characters or less.")
        else:
            updated = subjects + [{
                "name": name,
                "maximum": float(new_maximum)
            }]
            try:
                save_subjects(updated)
                st.session_state.subjects = updated
                st.success(f"{name} added successfully.")
                st.rerun()
            except (OSError, ValueError) as error:
                st.error(f"Could not save subject: {error}")

    st.divider()
    st.subheader("Edit or Remove a Subject")

    if subjects:
        selected_name = st.selectbox(
            "Select subject",
            [s["name"] for s in subjects],
            key="edit_subject_choice"
        )
        selected = next(
            s for s in subjects if s["name"] == selected_name
        )

        with st.form("edit_subject_form"):
            edited_name = st.text_input(
                "Updated subject name",
                value=selected["name"]
            )
            edited_maximum = st.number_input(
                "Updated maximum marks",
                min_value=1.0,
                max_value=10000.0,
                value=float(selected["maximum"]),
                step=1.0
            )
            col1, col2 = st.columns(2)
            with col1:
                edit_clicked = st.form_submit_button("Save Changes")
            with col2:
                remove_clicked = st.form_submit_button("Remove Subject")

        if edit_clicked:
            name = edited_name.strip()
            duplicate = any(
                s["name"].casefold() == name.casefold()
                and s["name"] != selected_name
                for s in subjects
            )

            if not name:
                st.error("Subject name cannot be empty.")
            elif len(name) > 80:
                st.error("Subject name is too long.")
            elif duplicate:
                st.error("Another subject already uses this name.")
            else:
                updated = [
                    {
                        "name": name if s["name"] == selected_name
                        else s["name"],
                        "maximum": float(edited_maximum)
                        if s["name"] == selected_name
                        else s["maximum"]
                    }
                    for s in subjects
                ]
                try:
                    save_subjects(updated)
                    st.session_state.subjects = updated
                    st.success("Subject updated.")
                    st.rerun()
                except (OSError, ValueError) as error:
                    st.error(f"Could not update subject: {error}")

        if remove_clicked:
            if len(subjects) <= 1:
                st.error("At least one subject must remain.")
            else:
                updated = [
                    s for s in subjects
                    if s["name"] != selected_name
                ]
                try:
                    save_subjects(updated)
                    st.session_state.subjects = updated
                    st.success("Subject removed from future mark entry.")
                    st.rerun()
                except (OSError, ValueError) as error:
                    st.error(f"Could not remove subject: {error}")

    st.warning(
        "Changing subjects does not rewrite older saved result records. "
        "Back up your files regularly."
    )


# ------------------ TAB 2: STUDENT MARKS ------------------

with tab_marks:
    st.header("Enter Student Marks")

    with st.form("student_marks_form"):
        student_name = st.text_input("Student full name")
        roll_number = st.text_input("Roll number")
        class_name = st.text_input("Class / Section")

        st.subheader("Subject-wise Marks")
        marks = {}

        for index, subject in enumerate(st.session_state.subjects):
            st.markdown(
                f"**{subject['name']}** — "
                f"Maximum: {subject['maximum']:g}"
            )
            marks[subject["name"]] = st.number_input(
                f"Obtained marks — {subject['name']}",
                min_value=0.0,
                max_value=float(subject["maximum"]),
                value=0.0,
                step=1.0,
                key=f"marks_{index}_{subject['name']}"
            )

        submit_result = st.form_submit_button(
            "Calculate and Save Result",
            type="primary"
        )

    if submit_result:
        name = student_name.strip()
        roll = roll_number.strip()
        class_value = class_name.strip()

        if not name:
            st.error("Student name is required.")
        elif len(name) > 120 or len(roll) > 50 or len(class_value) > 80:
            st.error("One of the student details is too long.")
        else:
            subject_list = st.session_state.subjects
            total_obtained = sum(marks[s["name"]] for s in subject_list)
            total_maximum = sum(s["maximum"] for s in subject_list)

            if total_maximum <= 0:
                st.error("Total maximum marks must be greater than zero.")
            else:
                percentage = total_obtained / total_maximum * 100

                record = {
                    "Student Name": name,
                    "Roll Number": roll,
                    "Class": class_value,
                    "Total Obtained": round(total_obtained, 2),
                    "Total Maximum": round(total_maximum, 2),
                    "Overall Percentage": round(percentage, 2),
                }

                for subject in subject_list:
                    subject_name = subject["name"]
                    obtained = marks[subject_name]
                    maximum = subject["maximum"]

                    record[f"{subject_name} Obtained"] = obtained
                    record[f"{subject_name} Maximum"] = maximum
                    record[f"{subject_name} Percentage"] = round(
                        obtained / maximum * 100, 2
                    )

                try:
                    save_result(record)
                    st.success("Student result saved successfully.")

                    st.subheader(f"Result: {name}")
                    result_table = pd.DataFrame([
                        {
                            "Subject": s["name"],
                            "Obtained": marks[s["name"]],
                            "Maximum": s["maximum"],
                            "Percentage": round(
                                marks[s["name"]] / s["maximum"] * 100, 2
                            )
                        }
                        for s in subject_list
                    ])

                    st.dataframe(
                        result_table,
                        hide_index=True,
                        use_container_width=True
                    )

                    col1, col2 = st.columns(2)
                    col1.metric(
                        "Total Marks",
                        f"{total_obtained:g} / {total_maximum:g}"
                    )
                    col2.metric("Overall Percentage", f"{percentage:.2f}%")

                    st.bar_chart(
                        result_table.set_index("Subject")["Percentage"]
                    )

                except (OSError, PermissionError, ValueError) as error:
                    st.error(f"Could not save result: {error}")


# ------------------ TAB 3: SAVED RESULTS ------------------

with tab_records:
    st.header("Saved Student Results")

    saved = load_results()

    if saved.empty:
        st.info("No student results have been saved yet.")
    else:
        st.dataframe(saved, use_container_width=True)

        csv_bytes = saved.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download All Results (CSV)",
            data=csv_bytes,
            file_name="student_results.csv",
            mime="text/csv"
        )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            saved.to_excel(writer, index=False, sheet_name="Student Results")

        st.download_button(
            "Download All Results (Excel)",
            data=output.getvalue(),
            file_name="student_results.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

st.divider()
st.caption(
    "Results are calculated as total obtained marks divided by "
    "total maximum marks, multiplied by 100. Pass/fail status is not "
    "assigned because school-specific passing rules may differ."
)
