import os
import streamlit as st
import pandas as pd
from google import genai

# ==========================================
# 1. PAGE & STYLING CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Engineering Degree OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for an Executive/Professional Aesthetic
st.markdown("""
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600;
        color: #495057;
    }
    
    /* Subtle Divider Lines */
    hr {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        border-top: 1px solid #dee2e6;
    }
    
    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #fafbfc;
        border-right: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA UTILITIES & CACHING
# ==========================================
DATA_DIR = "data"

@st.cache_data(ttl=60)
def load_csv(file_name):
    """Loads CSV dataset safely with error handling."""
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.error(f"Error parsing `{file_name}`: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_csv(df, file_name):
    """Saves DataFrame to CSV and clears cache."""
    path = os.path.join(DATA_DIR, file_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(path, index=False)
    st.cache_data.clear()
    st.success(f"Successfully saved to `{file_name}`!")

# Load Datasets
semesters_df = load_csv("semesters.csv")
courses_df = load_csv("courses.csv")
calendar_df = load_csv("academic_calendar.csv")
assessments_df = load_csv("assessments.csv")
scores_df = load_csv("scores.csv")
checklist_df = load_csv("plan_checklist.csv")

# Initialize default checklist if dataset missing or unformatted
if checklist_df.empty or "item" not in checklist_df.columns:
    checklist_df = pd.DataFrame([
        {"category": "Semester Preparation", "item": "Download current syllabus", "target_date": "2026-11-03", "status": "Done", "notes": "Saved PDF in drive"},
        {"category": "Assessments", "item": "Prepare for IA1-Data Structures", "target_date": "2026-11-09", "status": "In Progress", "notes": "Revise trees and graphs"},
        {"category": "Projects", "item": "Choose mini-project problem statement", "target_date": "2026-11-12", "status": "Not Started", "notes": "Brainstorm WebGL chemistry lab idea"},
        {"category": "Documents", "item": "Update resume and marksheets folder", "target_date": "2026-12-01", "status": "Not Started", "notes": "Include latest SGPA"},
        {"category": "Placement", "item": "Complete one aptitude mock test", "target_date": "2026-11-15", "status": "Not Started", "notes": "Focus on quantitative reasoning"},
        {"category": "Skills", "item": "Practice 5 LeetCode array problems", "target_date": "2026-11-20", "status": "In Progress", "notes": "Two-pointer technique"},
        {"category": "Labs", "item": "Complete Operating Systems lab manual", "target_date": "2026-11-22", "status": "Not Started", "notes": "CPU scheduling algorithms"}
    ])
    save_csv(checklist_df, "plan_checklist.csv")

# ==========================================
# 3. SIDEBAR NAVIGATION & QUICK SUMMARY
# ==========================================
st.sidebar.markdown("## 🎓 **Degree OS**")
st.sidebar.caption("Engineering Degree Command Center")
st.sidebar.markdown("---")

navigation = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Semesters 1-8",
        "Courses & Syllabus",
        "University Syllabus",
        "Academic / Leave Calendar",
        "Internal Assessments",
        "Status Tracker",
        "Scorecard",
        "Plan & Checklist",
        "Ask Degree AI",
        "Data Admin"
    ]
)

st.sidebar.markdown("---")

# Quick Sidebar Degree Meter
if not semesters_df.empty:
    total_c = semesters_df["total_credits"].sum()
    done_c = semesters_df["completed_credits"].sum()
    pct = round((done_c / total_c) * 100, 1) if total_c > 0 else 0
    st.sidebar.markdown(f"**Degree Progress:** `{pct}%`")
    st.sidebar.progress(float(done_c / total_c) if total_c > 0 else 0.0)

st.sidebar.caption("v1.0 • Streamlit & Gemini OS")

# ==========================================
# 1. DASHBOARD MODULE
# ==========================================
if navigation == "Dashboard":
    st.title("📌 Degree Command Center")
    st.caption("Real-time summary of academic standing, milestones, and upcoming schedules")

    # Compute KPI Metrics
    curr_sem = "3"
    total_credits = 0
    completed_credits = 0
    completion_pct = 0.0

    if not semesters_df.empty:
        total_credits = semesters_df["total_credits"].sum()
        completed_credits = semesters_df["completed_credits"].sum()
        if total_credits > 0:
            completion_pct = round((completed_credits / total_credits) * 100, 1)
        in_prog = semesters_df[semesters_df["status"] == "In Progress"]
        if not in_prog.empty:
            curr_sem = str(in_prog.iloc[0]["semester"])

    next_assessment = "None Scheduled"
    if not assessments_df.empty:
        planned_ass = assessments_df[assessments_df["status"] == "Planned"]
        if not planned_ass.empty:
            row = planned_ass.iloc[0]
            next_assessment = f"{row['course_code']} ({row['assessment_type']})"

    next_holiday = "None Scheduled"
    if not calendar_df.empty:
        holidays = calendar_df[calendar_df["event_type"] == "Holiday"]
        if not holidays.empty:
            h_row = holidays.iloc[0]
            next_holiday = f"{h_row['title']}"

    # Top KPI Metrics Display
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Active Semester", f"Semester {curr_sem}")
    c2.metric("Degree Progress", f"{completion_pct}%")
    c3.metric("Earned Credits", f"{completed_credits} / {total_credits}")
    c4.metric("Next Assessment", next_assessment)
    c5.metric("Next Holiday", next_holiday)

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 8-Semester Credit Distribution")
        if not semesters_df.empty:
            chart_df = semesters_df.copy()
            chart_df["Semester Label"] = "Sem " + chart_df["semester"].astype(str)
            st.bar_chart(
                data=chart_df,
                x="Semester Label",
                y=["completed_credits", "total_credits"],
                color=["#00CC96", "#636EFA"]
            )
        else:
            st.info("No semester datasets available.")

    with col_right:
        st.subheader("🎯 Performance Snapshot")
        if not scores_df.empty:
            avg_score = round(scores_df["score"].mean(), 2)
            st.metric("Test Average", f"{avg_score}%")
            st.markdown("**Recent Test Results:**")
            st.dataframe(
                scores_df[["course_code", "assessment_type", "grade"]].tail(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No assessment scores recorded.")

# ==========================================
# 2. SEMESTERS 1-8 MODULE
# ==========================================
elif navigation == "Semesters 1-8":
    st.title("📚 8-Semester Curriculum Map")
    st.caption("Overview of course counts, status, and credit weightage per semester")

    if not semesters_df.empty:
        cols = st.columns(4)
        for idx, row in semesters_df.iterrows():
            with cols[idx % 4]:
                st.markdown(f"### Semester {row['semester']}")
                status_color = "🟢" if row['status'] == "Completed" else ("🟡" if row['status'] == "In Progress" else "⚪")
                st.write(f"**Status:** {status_color} {row['status']}")
                st.write(f"**Credits:** {row['completed_credits']} / {row['total_credits']}")
                st.markdown("---")

        st.subheader("🔍 Detailed Semester Breakdown")
        selected_sem = st.selectbox("Filter by Semester", sorted(semesters_df["semester"].unique()))
        if not courses_df.empty:
            sem_courses = courses_df[courses_df["semester"] == selected_sem]
            st.dataframe(
                sem_courses[["course_code", "course_name", "credits", "status"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No semester dataset loaded.")

# ==========================================
# 3. COURSES & SYLLABUS MODULE
# ==========================================
elif navigation == "Courses & Syllabus":
    st.title("📖 Course Directory & Syllabus Topics")
    st.caption("Filter courses by semester to view detailed module topics and credit allocations")

    if not courses_df.empty:
        c1, c2 = st.columns([1, 2])
        with c1:
            sem_list = ["All Semesters"] + list(sorted(courses_df["semester"].unique()))
            selected_sem = st.selectbox("Select Semester", sem_list)
        with c2:
            search_query = st.text_input("🔍 Search Course Title or Code", "")

        filtered_df = courses_df.copy()
        if selected_sem != "All Semesters":
            filtered_df = filtered_df[filtered_df["semester"] == selected_sem]
        if search_query:
            filtered_df = filtered_df[
                filtered_df["course_name"].str.contains(search_query, case=False) |
                filtered_df["course_code"].str.contains(search_query, case=False)
            ]

        st.dataframe(
            filtered_df[["semester", "course_code", "course_name", "credits", "syllabus", "status"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No course datasets available.")

# ==========================================
# 4. UNIVERSITY SYLLABUS MODULE
# ==========================================
elif navigation == "University Syllabus":
    st.title("🏛️ Programme & University Syllabus Structure")
    st.caption("High-level department curriculum guidelines and official repository links")

    st.markdown("""
    #### Department of Computer Science & Engineering
    * **Degree Awarded:** Bachelor of Technology (B.Tech)
    * **Program Duration:** 4 Academic Years (8 Semesters)
    * **Total Curriculum Credits:** 179 Required Credits
    """)

    st.markdown("---")
    st.subheader("Official Curriculum Portal")
    syllabus_link = st.text_input(
        "University Syllabus Repository URL",
        value="https://github.com/vvaishnavi01/Engineering_degree_os"
    )
    st.info(f"🔗 Verified Portal Link: [{syllabus_link}]({syllabus_link})")

    if not courses_df.empty:
        st.markdown("### Master Course Index")
        st.dataframe(courses_df[["semester", "course_code", "course_name", "credits"]], use_container_width=True, hide_index=True)

# ==========================================
# 5. ACADEMIC / LEAVE CALENDAR MODULE
# ==========================================
elif navigation == "Academic / Leave Calendar":
    st.title("📅 Academic & Leave Schedule")
    st.caption("Important academic deadlines, mid-sem exam dates, and official college holidays")

    if not calendar_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            years = ["All Academic Years"] + list(calendar_df["academic_year"].unique())
            sel_year = st.selectbox("Filter Academic Year", years)
        with col2:
            sems = ["All Semesters"] + list(sorted(calendar_df["semester"].unique()))
            sel_sem = st.selectbox("Filter Semester", sems)

        cal_filtered = calendar_df.copy()
        if sel_year != "All Academic Years":
            cal_filtered = cal_filtered[cal_filtered["academic_year"] == sel_year]
        if sel_sem != "All Semesters":
            cal_filtered = cal_filtered[cal_filtered["semester"] == sel_sem]

        st.dataframe(cal_filtered, use_container_width=True, hide_index=True)
    else:
        st.info("No academic calendar events loaded.")

# ==========================================
# 6. INTERNAL ASSESSMENTS MODULE
# ==========================================
elif navigation == "Internal Assessments":
    st.title("📝 Internal Assessment Tracker")
    st.caption("Schedule for Internal Tests (IA1/IA2), assignments, lab evaluations, and project reviews")

    if not assessments_df.empty:
        st.dataframe(assessments_df, use_container_width=True, hide_index=True)
    else:
        st.info("No internal assessment records found.")

# ==========================================
# 7. STATUS TRACKER MODULE
# ==========================================
elif navigation == "Status Tracker":
    st.title("🚦 Course & Semester Status Tracker")
    st.caption("Track completion counts and view progress bars per semester")

    if not courses_df.empty:
        col1, col2, col3 = st.columns(3)
        completed_cnt = len(courses_df[courses_df["status"] == "Completed"])
        in_prog_cnt = len(courses_df[courses_df["status"] == "In Progress"])
        not_started_cnt = len(courses_df[courses_df["status"] == "Not Started"])

        col1.metric("Completed Courses", completed_cnt)
        col2.metric("In Progress", in_prog_cnt)
        col3.metric("Not Started", not_started_cnt)

        st.markdown("---")
        st.subheader("Semester Progress Bar Tracker")

        sem_options = sorted(courses_df["semester"].unique())
        selected_sem = st.selectbox("Select Semester for Progress Analysis", sem_options)

        sem_courses = courses_df[courses_df["semester"] == selected_sem]
        sem_total = len(sem_courses)
        sem_completed = len(sem_courses[sem_courses["status"] == "Completed"])

        if sem_total > 0:
            sem_pct = float(sem_completed / sem_total)
            st.write(f"**Semester {selected_sem} Completion:** {sem_completed} / {sem_total} Courses Completed ({int(sem_pct * 100)}%)")
            st.progress(sem_pct)

        st.markdown("---")
        st.subheader("Course Status Registry")
        st.dataframe(courses_df[["semester", "course_code", "course_name", "status"]], use_container_width=True, hide_index=True)
    else:
        st.info("No status data available.")

# ==========================================
# 8. SCORECARD MODULE
# ==========================================
elif navigation == "Scorecard":
    st.title("📊 Scorecard & Prototype Metrics")
    st.caption("Recorded test scores and overall prototype percentage calculations")

    if not scores_df.empty:
        st.dataframe(scores_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Aggregate Prototype Performance Metric")

        total_score = scores_df["score"].sum()
        total_max = scores_df["max_marks"].sum()
        if total_max > 0:
            proto_pct = round((total_score / total_max) * 100, 2)
            st.metric("Prototype Score Percentage", f"{proto_pct}%")

        st.warning("⚠️ **Note:** Calculated strictly as (Total Score / Total Max Marks) × 100. This is a prototype execution metric and does NOT represent an official university CGPA formula.")
    else:
        st.info("No score data recorded.")

# ==========================================
# 9. PLAN & CHECKLIST MODULE
# ==========================================
elif navigation == "Plan & Checklist":
    st.title("✅ Degree Execution Control Panel")
    st.caption("Manage custom milestones, exam preparation, documents, and placement readiness")

    # Summary Health Metrics
    total_items = len(checklist_df)
    done_items = len(checklist_df[checklist_df["status"] == "Done"]) if "status" in checklist_df.columns else 0
    in_prog_items = len(checklist_df[checklist_df["status"] == "In Progress"]) if "status" in checklist_df.columns else 0
    not_started_items = len(checklist_df[checklist_df["status"] == "Not Started"]) if "status" in checklist_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tasks", total_items)
    c2.metric("Done", done_items)
    c3.metric("In Progress", in_prog_items)
    c4.metric("Not Started", not_started_items)

    st.markdown("---")
    st.subheader("Interactive Task Management Panel")

    edited_checklist = st.data_editor(
        checklist_df,
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Not Started", "In Progress", "Done"],
                required=True
            )
        },
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("Save Checklist Changes"):
        save_csv(edited_checklist, "plan_checklist.csv")

# ==========================================
# 10. ASK DEGREE AI MODULE
# ==========================================
elif navigation == "Ask Degree AI":
    st.title("🤖 Ask Degree AI")
    st.caption("Grounded chatbot answering strictly from your loaded degree datasets")

    # Safely retrieve API key without crashing if secrets.toml is missing
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    user_query = st.text_input("Ask a question about your courses, dates, or checklist status:")

    if user_query:
        q_lower = user_query.lower()

        # Identify target data context
        sources_used = []
        if any(k in q_lower for k in ["course", "subject", "syllabus", "sem"]):
            sources_used.append("Courses")
        if any(k in q_lower for k in ["calendar", "holiday", "leave", "date", "event"]):
            sources_used.append("Calendar")
        if any(k in q_lower for k in ["assessment", "exam", "test", "ia", "assignment", "lab"]):
            sources_used.append("Assessments")
        if any(k in q_lower for k in ["score", "grade", "marks", "cgpa", "sgpa", "percentage"]):
            sources_used.append("Scores")
        if any(k in q_lower for k in ["checklist", "task", "todo", "plan", "milestone"]):
            sources_used.append("Plan")

        if not sources_used:
            sources_used = ["Courses", "Calendar", "Assessments", "Scores", "Plan"]

        st.info(f"📍 **Data Source(s) Consulted:** {', '.join(sources_used)}")

        if api_key:
            try:
                client = genai.Client(api_key=api_key)

                context_str = f"""
                SYSTEM INSTRUCTION: You are Degree AI, an intelligent academic copilot. 
                Answer strictly using ONLY the degree data supplied below. 
                Do NOT invent university rules, exam dates, marks, formulas, or syllabus content. 
                If the requested information is missing or cannot be verified from the data, respond with:
                "I cannot verify that from the current Degree OS data."

                DEGREE DATASETS CONTEXT:
                - Semesters: {semesters_df.to_dict(orient='records') if not semesters_df.empty else 'None'}
                - Courses: {courses_df.to_dict(orient='records') if not courses_df.empty else 'None'}
                - Academic Calendar: {calendar_df.to_dict(orient='records') if not calendar_df.empty else 'None'}
                - Assessments: {assessments_df.to_dict(orient='records') if not assessments_df.empty else 'None'}
                - Scores: {scores_df.to_dict(orient='records') if not scores_df.empty else 'None'}
                - Plan & Checklist: {checklist_df.to_dict(orient='records') if not checklist_df.empty else 'None'}
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{context_str}\n\nUser Question: {user_query}"
                )
                st.markdown("### 🤖 Answer:")
                st.write(response.text)

            except Exception as e:
                st.error(f"Error communicating with Gemini API: {e}")
        else:
            st.caption("💡 **Mode:** Local Grounded Fallback (GEMINI_API_KEY unconfigured)")
            st.markdown("### 🤖 Answer:")

            # Safe-AI Rule: Refuse unsupported or unverified policies
            if any(k in q_lower for k in ["official cgpa", "cgpa formula", "university rule", "regulation", "attendance policy"]):
                st.warning("I cannot verify that from the current Degree OS data.")
            elif "incomplete" in q_lower or ("subjects" in q_lower and "left" in q_lower) or ("courses" in q_lower and "left" in q_lower):
                if not courses_df.empty:
                    inc = courses_df[courses_df["status"] != "Completed"]
                    st.dataframe(inc[["semester", "course_code", "course_name", "status"]], use_container_width=True, hide_index=True)
                else:
                    st.write("No course records available.")
            elif "assessment" in q_lower or "exam" in q_lower or "ia" in q_lower or "test" in q_lower:
                if not assessments_df.empty:
                    st.dataframe(assessments_df[assessments_df["status"] == "Planned"], use_container_width=True, hide_index=True)
                else:
                    st.write("No upcoming assessments scheduled.")
            elif "holiday" in q_lower or "leave" in q_lower:
                if not calendar_df.empty:
                    holidays = calendar_df[calendar_df["event_type"] == "Holiday"]
                    st.dataframe(holidays, use_container_width=True, hide_index=True)
                else:
                    st.write("No upcoming holidays recorded.")
            elif "syllabus" in q_lower or "topic" in q_lower:
                if not courses_df.empty:
                    st.dataframe(courses_df[["course_code", "course_name", "syllabus"]], use_container_width=True, hide_index=True)
                else:
                    st.write("No syllabus details found.")
            elif "checklist" in q_lower or "task" in q_lower or "plan" in q_lower:
                if not checklist_df.empty:
                    st.dataframe(checklist_df[["category", "item", "status"]], use_container_width=True, hide_index=True)
                else:
                    st.write("No checklist data found.")
            else:
                st.warning("I cannot verify that from the current Degree OS data.")

# ==========================================
# 11. DATA ADMIN MODULE
# ==========================================
elif navigation == "Data Admin":
    st.title("⚙️ Data Administration Panel")
    st.caption("Inspect and directly modify base CSV data tables without editing application code")

    table_choice = st.selectbox(
        "Select Dataset to Edit",
        ["semesters.csv", "courses.csv", "academic_calendar.csv", "assessments.csv", "scores.csv", "plan_checklist.csv"]
    )

    current_df = load_csv(table_choice)

    if not current_df.empty:
        edited_df = st.data_editor(current_df, num_rows="dynamic", use_container_width=True)
        if st.button(f"Save Changes to {table_choice}"):
            save_csv(edited_df, table_choice)
    else:
        st.warning(f"File `{table_choice}` has no records or could not be loaded.")