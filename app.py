import requests
import json
import streamlit as st
from datetime import date

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


# Get students from n8n

webhook_url = "https://somvanshi.app.n8n.cloud/webhook-test/get-students"

students = []

try:
    payload = {
        "class": selected_class,
        "section": selected_section
    }

    response = requests.post(
        webhook_url,
        json=payload,
        timeout=30
    )

    if response.ok:
        result = response.json()
        students = result["rows"]
        if isinstance(students,str):
           students = json.loads(students)
    else:
           st.error(f"n8n error {response.status_code}:{response.text}")
except Exception as e:
    st.error(f"Unable to load students: {e}")

attendance = {}

for student in students:

    attendance[student["roll_no"]] = st.checkbox(
        f"{student['roll_no']} - {student['name']}",
        value=True
    )

st.divider()

if st.button(
    "✅ Submit Attendance",
    use_container_width=True
):

    st.success("Attendance submitted successfully!")

    st.write("### Attendance Summary")

    for student in students:

        if attendance[student["roll_no"]]:
            status = "Present"
        else:
            status = "Absent"

        st.write(
            f'{student["roll_no"]} - '
            f'{student["name"]} → **{status}**'
        )
# --------------------------------
# n8n Connection Test
# --------------------------------

st.divider()

st.subheader("🧪 n8n Connection Test")

if st.button("Test n8n Connection"):

    webhook_url = "https://somvanshi.app.n8n.cloud/webhook-test/get-students"

    payload = {
        "class": selected_class,
        "section": selected_section
    }

    try:

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=30
        )

        st.write("Status Code:", response.status_code)

        if response.ok:
            st.success("✅ n8n connection successful!")

            try:
                st.json(response.json())
            except:
                st.write(response.text)

        else:
            st.error("❌ n8n returned an error")
            st.write(response.text)

    except Exception as e:
        st.error("❌ Connection failed")
        st.write(str(e))
    

