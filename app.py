
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from io import StringIO

from ai_engine import generate_project_report


# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="AI Project Management Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Project Management Assistant")

st.caption(
    "An AI-powered tool for project monitoring, "
    "risk identification and automated reporting."
)

st.divider()


# -----------------------------------
# SAMPLE DATA
# -----------------------------------

@st.cache_data
def load_sample_data():
    return pd.read_csv("sample_updates.csv")


# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Project Settings")

project_name = st.sidebar.text_input(
    "Project Name",
    value="AI Platform Development"
)

st.sidebar.write("Upload project updates below.")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)


# -----------------------------------
# LOAD DATA
# -----------------------------------

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = load_sample_data()

except Exception as error:
    st.error(f"Unable to read CSV: {error}")
    st.stop()


required_columns = [
    "Task",
    "Owner",
    "Status",
    "Progress",
    "Due_Date",
    "Dependency",
    "Update"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Missing columns: " + ", ".join(missing_columns)
    )
    st.stop()

if df.empty:
    st.warning("The uploaded CSV contains no tasks.")
    st.stop()

df["Progress"] = pd.to_numeric(
    df["Progress"], errors="coerce"
)

if df["Progress"].isna().any():
    st.error("Progress must contain valid numeric values.")
    st.stop()

if not df["Progress"].between(0, 100).all():
    st.error("Progress must be between 0 and 100.")
    st.stop()

df["Due_Date"] = pd.to_datetime(
    df["Due_Date"], errors="coerce"
)

if df["Due_Date"].isna().any():
    st.error("Please provide valid due dates.")
    st.stop()

df["Status"] = df["Status"].astype(str).str.strip()

valid_statuses = [
    "Completed",
    "In Progress",
    "Delayed",
    "Pending"
]

if not df["Status"].isin(valid_statuses).all():
    st.error(
        "Status must be Completed, In Progress, "
        "Delayed or Pending."
    )
    st.stop()


# -----------------------------------
# METRICS
# -----------------------------------

total_tasks = len(df)

completed = (df["Status"] == "Completed").sum()

in_progress = (df["Status"] == "In Progress").sum()

delayed = (df["Status"] == "Delayed").sum()

pending = (df["Status"] == "Pending").sum()

average_progress = df["Progress"].mean()

st.subheader(project_name)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Tasks", total_tasks)
col2.metric("Completed", int(completed))
col3.metric("In Progress", int(in_progress))
col4.metric("Delayed", int(delayed))
col5.metric("Average Progress", f"{average_progress:.0f}%")


# -----------------------------------
# CHARTS
# -----------------------------------

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("Task Status Distribution")

    status_counts = (
        df["Status"]
        .value_counts()
        .reindex(valid_statuses, fill_value=0)
        .reset_index()
    )

    status_counts.columns = ["Status", "Count"]

    fig = px.pie(
        status_counts,
        names="Status",
        values="Count",
        hole=0.45,
        title="Current Task Status"
    )

    st.plotly_chart(fig, use_container_width=True)


with right:

    st.subheader("Task Progress")

    fig2 = px.bar(
        df,
        x="Task",
        y="Progress",
        color="Status",
        range_y=[0, 100],
        title="Progress by Task"
    )

    st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------
# TASK TABLE
# -----------------------------------

st.divider()

st.subheader("Project Task Overview")

display_df = df.copy()

display_df["Due_Date"] = (
    display_df["Due_Date"].dt.strftime("%Y-%m-%d")
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# -----------------------------------
# SIMPLE RISK DETECTION
# -----------------------------------

st.divider()

st.subheader("Rule-Based Risk Indicators")

today = pd.Timestamp(date.today())

overdue = df[
    (df["Due_Date"] < today)
    & (df["Status"] != "Completed")
]

if delayed > 0:
    st.warning(
        f"{delayed} task(s) have been marked as delayed."
    )

if not overdue.empty:
    st.error(
        f"{len(overdue)} unfinished task(s) "
        "have passed their due dates."
    )

if delayed == 0 and overdue.empty:
    st.success("No delayed or overdue tasks detected.")

st.caption(
    "These indicators use project data and date rules. "
    "They are separate from Gemini's AI analysis."
)


# -----------------------------------
# GEMINI AI ANALYSIS
# -----------------------------------

st.divider()

st.header("🤖 AI Project Analysis")

st.write(
    "Generate an AI-powered project report using "
    "the uploaded project information."
)

if st.button(
    "Generate AI Project Report",
    type="primary",
    use_container_width=True
):

    project_data = df.to_csv(index=False)

    with st.spinner(
        "Gemini is analyzing project information..."
    ):

        try:

            report = generate_project_report(
                project_data
            )

            st.session_state["project_report"] = report
            st.session_state["report_source"] = project_data

        except Exception as error:

            st.error(
                f"Unable to generate report: {error}"
            )


# -----------------------------------
# DISPLAY REPORT
# -----------------------------------

if "project_report" in st.session_state:

    st.subheader("Generated Project Report")

    st.markdown(st.session_state["project_report"])

    st.info(
        "Please review all AI-generated findings "
        "against the original project data before sharing."
    )

    reviewed = st.checkbox(
        "I have reviewed this report against the source data."
    )

    if reviewed:

        st.download_button(
            label="Download Project Report",
            data=st.session_state["project_report"],
            file_name="project_status_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    else:

        st.caption(
            "Review the report before enabling its download."
        )


# -----------------------------------
# DOWNLOAD SOURCE DATA
# -----------------------------------

st.divider()

st.subheader("Export Project Data")

csv_data = df.to_csv(index=False)

st.download_button(
    "Download Project Data",
    data=csv_data,
    file_name="project_updates.csv",
    mime="text/csv"
)

st.caption(
    "AI-generated insights are decision-support suggestions, "
    "not substitutes for project owner approval."
)
