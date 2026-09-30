import json
import requests
import streamlit as st
from datetime import date

# ---------------- n8n URLs (production) ----------------
GET_STUDENTS_URL = "https://somvanshi.app.n8n.cloud/webhook-test/get-students"
SAVE_ATTENDANCE_URL = "https://somvanshi.app.n8n.cloud/webhook-test/save-attendance"

st.set_page_config(
    page_title="Attendance System",
    page_icon="📋",
    layout="centered"
)

st.title("📋 Attendance System")
st.write("Teacher Attendance Dashboard")

st.divider()

# Class, Section and Subject
col1, col2 = st.columns(2)

with col1:
    selected_class = st.selectbox(
        "Class",
        ["BCA 1", "BCA 2", "BCA 3"]
    )

with col2:
    selected_section = st.selectbox(
        "Section",
        ["A", "B", "C"]
    )

subject = st.selectbox(
    "Subject",
    [
        "DBMS",
        "Operating System",
        "Computer Networks",
        "Python"
    ]
)

attendance_date = st.date_input(
    "Date",
    value=date.today()
)

st.divider()

st.subheader("👨‍🎓 Mark Attendance")


# ---------------- Get students from n8n ----------------
@st.cache_data(ttl=60, show_spinner="Loading students...")
def load_students(cls, section):
    payload = {
        "class": cls,
        "section": section
    }
    response = requests.post(
        GET_STUDENTS_URL,
        json=payload,
        timeout=30
    )
    if not response.ok:
        raise Exception(f"n8n error {response.status_code}: {response.text}")

    result = response.json()
    rows = result["rows"]
    if isinstance(rows, str):
        rows = json.loads(rows)
    return rows


students = []

try:
    students = load_students(selected_class, selected_section)
except Exception as e:
    st.error(f"Unable to load students: {e}")

attendance = {}

for student in students:
    attendance[student["roll_no"]] = st.checkbox(
        f"{student['roll_no']} - {student['name']}",
        value=True,
        key=f"att_{selected_class}_{selected_section}_{student['roll_no']}"
    )

st.divider()

# ---------------- Submit attendance ----------------
if st.button("✅ Submit Attendance", use_container_width=True):

    if not students:
        st.warning("No students found to submit.")
    else:
        records = [
            {
                "roll_no": s["roll_no"],
                "name": s["name"],
                "status": "Present" if attendance[s["roll_no"]] else "Absent"
            }
            for s in students
        ]

        save_payload = {
            "class": selected_class,
            "section": selected_section,
            "subject": subject,
            "date": str(attendance_date),
            "records": records
        }

        try:
            res = requests.post(
                SAVE_ATTENDANCE_URL,
                json=save_payload,
                timeout=30
            )

            if res.ok:
                st.success("Attendance submitted successfully!")

                st.write("### Attendance Summary")
                for r in records:
                    st.write(
                        f"{r['roll_no']} - {r['name']} → {r['status']}"
                    )
            else:
                st.error(f"Save failed: {res.status_code}")
                st.write(res.text)

        except Exception as e:
            st.error(f"Error while saving: {e}")

# ---------------- n8n Connection Test ----------------
st.divider()

st.subheader("🧪 n8n Connection Test")

if st.button("Test n8n Connection"):

    payload = {
        "class": selected_class,
        "section": selected_section
    }

    try:
        response = requests.post(
            GET_STUDENTS_URL,
            json=payload,
            timeout=30
        )

        st.write("Status Code:", response.status_code)

        if response.ok:
            st.success("✅ n8n connection successful!")
            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)
        else:
            st.error("❌ n8n returned an error")
            st.write(response.text)
    except Exception as e:
        st.error("❌ Connection failed")
        st.write(str(e))
             
