import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="FuturePath AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# =====================================
# DATA CLEANING
# =====================================
def process_dataframe(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    if "annual_salary_usd" in df.columns:
        df["annual_salary_usd"] = pd.to_numeric(
            df["annual_salary_usd"],
            errors="coerce"
        )

    return df

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():
    jobs = pd.read_csv(
    "data/processed/ai_jobs_market_2025_2026_clean.csv"
    )
    
    roles = pd.read_csv(
        "data/processed/it_job_roles_skills_clean.csv"
    )
    
    career = pd.read_csv(
        "data/processed/skill_career_recommendation_clean.csv"
    )

    jobs = process_dataframe(jobs)
    roles = process_dataframe(roles)
    career = process_dataframe(career)

    return jobs, roles, career

try:
    df_jobs, df_roles, df_career = load_data()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# =====================================
# HEADER
# =====================================
st.title("🚀 FuturePath AI Dashboard")
st.markdown("### AI Career Analytics, Skill Insights & Career Recommendation")
st.write("Explore AI jobs, IT skills, and career opportunities.")

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("📌 Navigation")
menu = st.sidebar.radio(
    "Choose Dashboard",
    [
        "AI Jobs Market",
        "IT Roles & Skills",
        "Career Recommendation"
    ]
)

# =====================================
# AI JOBS MARKET
# =====================================
if menu == "AI Jobs Market":

    st.header("📊 AI Jobs Market Analysis")

    # FILTERS
    st.sidebar.subheader("🔍 Filter Data")

    country = []
    if "country" in df_jobs.columns:
        country = st.sidebar.multiselect(
            "Country",
            sorted(df_jobs["country"].dropna().unique())
        )

    exp_level = []
    if "experience_level" in df_jobs.columns:
        exp_level = st.sidebar.multiselect(
            "Experience Level",
            sorted(df_jobs["experience_level"].dropna().unique())
        )

    category = []
    if "job_category" in df_jobs.columns:
        category = st.sidebar.multiselect(
            "Job Category",
            sorted(df_jobs["job_category"].dropna().unique())
        )

    filtered_df = df_jobs.copy()

    if country:
        filtered_df = filtered_df[
            filtered_df["country"].isin(country)
        ]

    if exp_level:
        filtered_df = filtered_df[
            filtered_df["experience_level"].isin(exp_level)
        ]

    if category:
        filtered_df = filtered_df[
            filtered_df["job_category"].isin(category)
        ]

    # SEARCH JOB
    search = st.text_input("🔍 Search Job Title")

    if search and "job_title" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["job_title"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", len(filtered_df))

    with col2:
        st.metric(
            "Countries",
            filtered_df["country"].nunique()
            if "country" in filtered_df.columns else 0
        )

    with col3:
        st.metric(
            "Job Titles",
            filtered_df["job_title"].nunique()
            if "job_title" in filtered_df.columns else 0
        )

    with col4:
        if "annual_salary_usd" in filtered_df.columns:
            avg_salary = filtered_df[
                "annual_salary_usd"
            ].mean()

            st.metric(
                "Avg Salary",
                f"${avg_salary:,.0f}"
            )

    # DATA PREVIEW
    with st.expander("📁 Dataset Preview"):
        st.dataframe(filtered_df.head(20))

    # CHARTS
    col1, col2 = st.columns(2)

    with col1:
        if "experience_level" in filtered_df.columns:
            st.subheader("Experience Level")
            exp_counts = (
                filtered_df["experience_level"]
                .value_counts()
                .reset_index()
            )
            exp_counts.columns = ["level", "count"]

            fig = px.bar(
                exp_counts,
                x="level",
                y="count"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "job_category" in filtered_df.columns:
            st.subheader("Top Job Categories")
            fig = px.pie(
                filtered_df,
                names="job_category"
            )
            st.plotly_chart(fig, use_container_width=True)

    # SALARY DISTRIBUTION
    if "annual_salary_usd" in filtered_df.columns:
        st.subheader("💰 Salary Distribution")
        fig = px.histogram(
            filtered_df,
            x="annual_salary_usd"
        )
        st.plotly_chart(fig, use_container_width=True)

    # TOP SKILLS
    if "required_skills" in filtered_df.columns:
        st.subheader("🛠️ Top Required Skills")

        skills = (
            filtered_df["required_skills"]
            .fillna("")
            .str.split(r"\s*\|\s*")
            .explode()
            .str.strip()
        )

        top_skills = skills.value_counts().head(10)

        fig = px.bar(
            x=top_skills.values,
            y=top_skills.index,
            orientation="h"
        )

        st.plotly_chart(fig, use_container_width=True)

    # DOWNLOAD CSV
    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Filtered Dataset",
        data=csv,
        file_name="filtered_ai_jobs.csv",
        mime="text/csv"
    )

# =====================================
# IT ROLES & SKILLS
# =====================================
elif menu == "IT Roles & Skills":

    st.header("💻 IT Roles & Skills")

    search_role = st.text_input("🔍 Search Job Role")

    temp_df = df_roles.copy()

    if search_role and "job_title" in temp_df.columns:
        temp_df = temp_df[
            temp_df["job_title"]
            .astype(str)
            .str.contains(search_role, case=False, na=False)
        ]

    st.dataframe(temp_df.head(20))

    if not temp_df.empty and "job_title" in temp_df.columns:
        selected_role = st.selectbox(
            "Select Role",
            temp_df["job_title"].dropna().unique()
        )

        role_info = temp_df[
            temp_df["job_title"] == selected_role
        ].iloc[0]

        st.subheader("📌 Job Description")
        st.write(role_info.get("job_description", "-"))

        st.subheader("🛠️ Skills")
        st.write(role_info.get("skills", "-"))

        st.subheader("🎓 Certifications")
        st.write(role_info.get("certifications", "-"))

# =====================================
# CAREER RECOMMENDATION
# =====================================
elif menu == "Career Recommendation":

    st.header("🎯 Career Recommendation")

    logical = st.slider(
        "Logical Intelligence",
        0, 100, 50
    )

    linguistic = st.slider(
        "Linguistic Intelligence",
        0, 100, 50
    )

    interpersonal = st.slider(
        "Interpersonal Intelligence",
        0, 100, 50
    )

    st.subheader("🚀 Recommended Career")

    if logical >= 70:
        st.success("✅ AI Engineer / Data Scientist")
    elif linguistic >= 70:
        st.success("✅ Business Analyst / Product Manager")
    elif interpersonal >= 70:
        st.success("✅ Project Manager / HR Specialist")
    else:
        st.info("✅ Software Engineer / IT Support")

    with st.expander("Career Dataset Preview"):
        st.dataframe(df_career.head(20))

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("FuturePath AI Dashboard | Developed by Data Science Team © 2026")
