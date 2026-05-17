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
# CUSTOM CSS
# =====================================
st.markdown('''
<style>
.metric-card {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style>
''', unsafe_allow_html=True)

# =====================================
# CLEAN DATA
# =====================================
def process_dataframe(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
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
    jobs = pd.read_csv("ai_jobs_market_2025_2026_clean.csv")
    roles = pd.read_csv("it_job_roles_skills_clean.csv")
    career = pd.read_csv("skill_career_recommendation_clean.csv")

    jobs = process_dataframe(jobs)
    roles = process_dataframe(roles)
    career = process_dataframe(career)

    return jobs, roles, career

try:
    df_jobs, df_roles, df_career = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# =====================================
# HEADER
# =====================================
st.title("🚀 FuturePath AI Dashboard")
st.markdown("### AI Career Analytics, Skill Insights & Career Recommendation")
st.markdown("Explore AI job trends, IT skills, and future career recommendations.")

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
# DASHBOARD 1
# =====================================
if menu == "AI Jobs Market":

    st.header("📊 AI Jobs Market Analysis")

    # FILTERS
    st.sidebar.subheader("🔍 Filter Data")

    country = st.sidebar.multiselect(
        "Country",
        options=sorted(df_jobs['country'].dropna().unique())
        if 'country' in df_jobs.columns else []
    )

    exp_level = st.sidebar.multiselect(
        "Experience Level",
        options=sorted(df_jobs['experience_level'].dropna().unique())
        if 'experience_level' in df_jobs.columns else []
    )

    category = st.sidebar.multiselect(
        "Job Category",
        options=sorted(df_jobs['job_category'].dropna().unique())
        if 'job_category' in df_jobs.columns else []
    )

    filtered_df = df_jobs.copy()

    if country:
        filtered_df = filtered_df[
            filtered_df['country'].isin(country)
        ]

    if exp_level:
        filtered_df = filtered_df[
            filtered_df['experience_level'].isin(exp_level)
        ]

    if category:
        filtered_df = filtered_df[
            filtered_df['job_category'].isin(category)
        ]

    # SEARCH
    search = st.text_input("🔍 Search Job Title")

    if search and 'job_title' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['job_title']
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    # KPI
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Jobs", len(filtered_df))

    c2.metric(
        "Countries",
        filtered_df['country'].nunique()
        if 'country' in filtered_df.columns else 0
    )

    c3.metric(
        "Unique Job Titles",
        filtered_df['job_title'].nunique()
        if 'job_title' in filtered_df.columns else 0
    )

    c4.metric(
        "Avg Salary",
        f"${filtered_df['annual_salary_usd'].mean():,.0f}"
        if 'annual_salary_usd' in filtered_df.columns else "N/A"
    )

    st.divider()

    # PREVIEW
    with st.expander("📁 Dataset Preview"):
        st.dataframe(filtered_df.head(20))

    # VISUALS
    col1, col2 = st.columns(2)

    with col1:
        if 'experience_level' in filtered_df.columns:
            st.subheader("Experience Level")
            fig = px.bar(
                filtered_df['experience_level']
                .value_counts()
                .reset_index(),
                x='count',
                y='experience_level',
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'job_category' in filtered_df.columns:
            st.subheader("Top Job Categories")
            fig = px.pie(
                filtered_df,
                names='job_category'
            )
            st.plotly_chart(fig, use_container_width=True)

    # SALARY
    if 'annual_salary_usd' in filtered_df.columns:
        st.subheader("💰 Salary Distribution")
        fig = px.histogram(
            filtered_df,
            x='annual_salary_usd'
        )
        st.plotly_chart(fig, use_container_width=True)

    # SKILLS
    if 'required_skills' in filtered_df.columns:
        st.subheader("🛠️ Top Required Skills")

        skills = (
            filtered_df['required_skills']
            .fillna('')
            .str.split(r'\s*\|\s*')
            .explode()
        )

        top_skills = skills.value_counts().head(15)

        fig = px.bar(
            top_skills,
            x=top_skills.values,
            y=top_skills.index,
            orientation='h'
        )

        st.plotly_chart(fig, use_container_width=True)

    # DOWNLOAD
    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Filtered Dataset",
        data=csv,
        file_name="filtered_ai_jobs.csv",
        mime="text/csv"
    )

# =====================================
# DASHBOARD 2
# =====================================
elif menu == "IT Roles & Skills":

    st.header("💻 IT Roles & Skills")

    search_role = st.text_input("🔍 Search Role")

    temp_df = df_roles.copy()

    if search_role:
        temp_df = temp_df[
            temp_df['job_title']
            .astype(str)
            .str.contains(search_role, case=False, na=False)
        ]

    st.dataframe(temp_df.head(20))

    if not temp_df.empty:
        selected_role = st.selectbox(
            "Select Role",
            temp_df['job_title'].dropna().unique()
        )

        role_info = temp_df[
            temp_df['job_title'] == selected_role
        ].iloc[0]

        st.subheader("📌 Job Description")
        st.write(role_info.get('job_description', '-'))

        st.subheader("🛠️ Skills")
        st.write(role_info.get('skills', '-'))

        st.subheader("🎓 Certifications")
        st.write(role_info.get('certifications', '-'))

# =====================================
# DASHBOARD 3
# =====================================
elif menu == "Career Recommendation":

    st.header("🎯 Career Recommendation")

    st.write("Input your intelligence preference")

    logical = st.slider("Logical Intelligence", 0, 100, 50)
    linguistic = st.slider("Linguistic Intelligence", 0, 100, 50)
    interpersonal = st.slider("Interpersonal Intelligence", 0, 100, 50)

    st.subheader("🚀 Recommended Career")

    if logical > 70:
        st.success("Data Scientist / AI Engineer")
    elif linguistic > 70:
        st.success("Business Analyst / Product Manager")
    elif interpersonal > 70:
        st.success("Project Manager / HR Tech")
    else:
        st.info("Software Engineer / IT Support")

    st.dataframe(df_career.head(20))

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("FuturePath AI Dashboard | Developed by Data Science Team © 2026")
```

### Cara pakai

1. Replace `app.py` lama
2. Pastikan nama CSV sama persis
3. Commit & push ke GitHub
4. Redeploy Streamlit
