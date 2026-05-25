import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="FuturePath AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
.main-title{
    font-size:40px;
    font-weight:bold;
    color:#4F46E5;
}

.sub-title{
    font-size:18px;
    color:gray;
}

.metric-box{
    background-color:#f8f9fa;
    padding:15px;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA CLEANING
# ==========================================
def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def convert_numeric(df):
    numeric_cols = [
        "annual_salary_usd",
        "salary_usd",
        "salary"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


# ==========================================
# LOAD DATA
# ==========================================
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

    jobs = clean_columns(jobs)
    roles = clean_columns(roles)
    career = clean_columns(career)

    jobs = convert_numeric(jobs)

    return jobs, roles, career


try:
    df_jobs, df_roles, df_career = load_data()

except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# ==========================================
# HEADER
# ==========================================
st.markdown(
    '<p class="main-title">🚀 FuturePath AI Dashboard</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">AI Career Analytics, Skill Recommendation & Career Navigation</p>',
    unsafe_allow_html=True
)

st.markdown("---")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("📌 Navigation")

menu = st.sidebar.radio(
    "Choose Dashboard",
    [
        "AI Jobs Market",
        "IT Roles & Skills",
        "Smart Career Recommendation",
        "Skill Gap Analysis",
        "Career Navigation",
        "Salary Explorer",
        "Learning Recommendation"
    ]
)

# ==========================================
# AI JOBS MARKET
# ==========================================
if menu == "AI Jobs Market":

    st.header("📊 AI Jobs Market Analysis")

    st.sidebar.subheader("🔍 Filters")

    filtered_df = df_jobs.copy()

    # COUNTRY
    if "country" in df_jobs.columns:
        country = st.sidebar.multiselect(
            "Country",
            sorted(
                df_jobs["country"]
                .dropna()
                .unique()
            )
        )

        if country:
            filtered_df = filtered_df[
                filtered_df["country"].isin(country)
            ]

    # EXPERIENCE
    if "experience_level" in df_jobs.columns:
        exp_level = st.sidebar.multiselect(
            "Experience Level",
            sorted(
                df_jobs["experience_level"]
                .dropna()
                .unique()
            )
        )

        if exp_level:
            filtered_df = filtered_df[
                filtered_df[
                    "experience_level"
                ].isin(exp_level)
            ]

    # CATEGORY
    if "job_category" in df_jobs.columns:
        category = st.sidebar.multiselect(
            "Job Category",
            sorted(
                df_jobs["job_category"]
                .dropna()
                .unique()
            )
        )

        if category:
            filtered_df = filtered_df[
                filtered_df[
                    "job_category"
                ].isin(category)
            ]

    # SEARCH
    search = st.text_input(
        "🔍 Search Job Title"
    )

    if search and "job_title" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["job_title"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Jobs",
            len(filtered_df)
        )

    with col2:
        st.metric(
            "Countries",
            filtered_df["country"].nunique()
            if "country" in filtered_df.columns
            else 0
        )

    with col3:
        st.metric(
            "Job Titles",
            filtered_df["job_title"].nunique()
            if "job_title" in filtered_df.columns
            else 0
        )

    with col4:
        if "annual_salary_usd" in filtered_df.columns:
            avg_salary = (
                filtered_df[
                    "annual_salary_usd"
                ].mean()
            )

            st.metric(
                "Avg Salary",
                f"${avg_salary:,.0f}"
            )

    st.markdown("---")

    # DATA PREVIEW
    with st.expander("📁 Dataset Preview"):
        st.dataframe(filtered_df)

    # CHARTS
    col1, col2 = st.columns(2)

    with col1:
        if "experience_level" in filtered_df.columns:

            exp_counts = (
                filtered_df[
                    "experience_level"
                ]
                .value_counts()
                .reset_index()
            )

            exp_counts.columns = [
                "Level",
                "Count"
            ]

            fig = px.bar(
                exp_counts,
                x="Level",
                y="Count",
                title="Experience Level"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with col2:
        if "job_category" in filtered_df.columns:

            fig = px.pie(
                filtered_df,
                names="job_category",
                title="Job Category"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # SALARY DISTRIBUTION
    if "annual_salary_usd" in filtered_df.columns:

        st.subheader(
            "💰 Salary Distribution"
        )

        fig = px.histogram(
            filtered_df,
            x="annual_salary_usd",
            nbins=30
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # TOP SKILLS
    if "required_skills" in filtered_df.columns:

        st.subheader(
            "🔥 Top Demanded Skills"
        )

        skills = (
            filtered_df[
                "required_skills"
            ]
            .fillna("")
            .str.split(r"\s*\|\s*")
            .explode()
            .str.strip()
        )

        top_skills = (
            skills.value_counts()
            .head(10)
        )

        fig = px.bar(
            x=top_skills.values,
            y=top_skills.index,
            orientation="h",
            title="Top 10 Skills"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    csv = filtered_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇ Download Dataset",
        data=csv,
        file_name="filtered_jobs.csv",
        mime="text/csv"
    )

# ==========================================
# IT ROLES & SKILLS
# ==========================================
elif menu == "IT Roles & Skills":

    st.header("💻 IT Roles & Skills")

    search_role = st.text_input(
        "🔍 Search Job Role"
    )

    temp_df = df_roles.copy()

    if (
        search_role
        and "job_title" in temp_df.columns
    ):
        temp_df = temp_df[
            temp_df["job_title"]
            .astype(str)
            .str.contains(
                search_role,
                case=False,
                na=False
            )
        ]

    st.dataframe(temp_df.head(20))

    if (
        not temp_df.empty
        and "job_title"
        in temp_df.columns
    ):

        selected_role = st.selectbox(
            "Select Role",
            temp_df[
                "job_title"
            ]
            .dropna()
            .unique()
        )

        role_info = temp_df[
            temp_df["job_title"]
            == selected_role
        ].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(
                "📌 Job Description"
            )

            st.write(
                role_info.get(
                    "job_description",
                    "-"
                )
            )

            st.subheader(
                "🛠️ Skills"
            )

            st.write(
                role_info.get(
                    "skills",
                    "-"
                )
            )

        with col2:
            st.subheader(
                "🎓 Certifications"
            )

            st.write(
                role_info.get(
                    "certifications",
                    "-"
                )
            )

            st.subheader(
                "📈 Role Information"
            )

            st.info(
                f"Selected Role: {selected_role}"
            )


# ==========================================
# SMART CAREER RECOMMENDATION
# ==========================================
elif menu == "Smart Career Recommendation":

    st.header(
        "🎯 Smart Career Recommendation"
    )

    st.write(
        "Adjust your intelligence score "
        "to discover the best career path."
    )

    col1, col2 = st.columns(2)

    with col1:

        logical = st.slider(
            "Logical Intelligence",
            0,
            100,
            50
        )

        technical = st.slider(
            "Technical Skill",
            0,
            100,
            50
        )

    with col2:

        linguistic = st.slider(
            "Linguistic Intelligence",
            0,
            100,
            50
        )

        interpersonal = st.slider(
            "Interpersonal Skill",
            0,
            100,
            50
        )

    recommendations = {
        "AI Engineer":
            logical * 0.35
            + technical * 0.45
            + linguistic * 0.10
            + interpersonal * 0.10,

        "Data Scientist":
            logical * 0.40
            + technical * 0.35
            + linguistic * 0.15
            + interpersonal * 0.10,

        "Software Engineer":
            logical * 0.30
            + technical * 0.40
            + interpersonal * 0.20
            + linguistic * 0.10,

        "Business Analyst":
            linguistic * 0.30
            + interpersonal * 0.30
            + logical * 0.25
            + technical * 0.15,

        "Project Manager":
            interpersonal * 0.45
            + linguistic * 0.30
            + logical * 0.15
            + technical * 0.10
    }

    result_df = pd.DataFrame(
        recommendations.items(),
        columns=[
            "Career",
            "Score"
        ]
    )

    result_df = (
        result_df
        .sort_values(
            by="Score",
            ascending=False
        )
        .head(3)
    )

    st.subheader(
        "🚀 Top 3 Recommendation"
    )

    for i, row in (
        result_df.iterrows()
    ):

        st.success(
            f"{row['Career']} "
            f"({row['Score']:.1f}%)"
        )

    fig = px.bar(
        result_df,
        x="Career",
        y="Score",
        title="Career Match Score"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# SKILL GAP ANALYSIS
# ==========================================
elif menu == "Skill Gap Analysis":

    st.header(
        "🔥 Skill Gap Analysis"
    )

    if (
        "job_title"
        in df_roles.columns
    ):

        target_role = st.selectbox(
            "Choose Target Role",
            sorted(
                df_roles[
                    "job_title"
                ]
                .dropna()
                .unique()
            )
        )

        role_data = df_roles[
            df_roles["job_title"]
            == target_role
        ]

        if not role_data.empty:

            skill_text = str(
                role_data.iloc[0].get(
                    "skills",
                    ""
                )
            )

            role_skills = list(
                set([
                    x.strip()
                    for x in
                    skill_text.split(",")
                    if x.strip()
                ])
            )

            user_skill = st.multiselect(
                "Select Your Skills",
                sorted(role_skills)
            )

            matched = list(
                set(user_skill)
                & set(role_skills)
            )

            missing = list(
                set(role_skills)
                - set(user_skill)
            )

            match_percent = (
                len(matched)
                / len(role_skills)
                * 100
            ) if role_skills else 0

            st.metric(
                "Skill Match %",
                f"{match_percent:.1f}%"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader(
                    "✅ Skills You Have"
                )

                for skill in matched:
                    st.success(skill)

            with col2:
                st.subheader(
                    "❌ Missing Skills"
                )

                for skill in missing:
                    st.error(skill)

# ==========================================
# CAREER NAVIGATION
# ==========================================
elif menu == "Career Navigation":

    st.header(
        "🧭 Career Navigation"
    )

    career_paths = {
        "Data Science": [
            "Junior Data Analyst",
            "Data Analyst",
            "Data Scientist",
            "AI Engineer"
        ],

        "Software Engineering": [
            "Junior Developer",
            "Software Engineer",
            "Senior Engineer",
            "Software Architect"
        ],

        "Cybersecurity": [
            "IT Support",
            "Security Analyst",
            "Cybersecurity Engineer",
            "Security Architect"
        ],

        "Cloud Computing": [
            "System Administrator",
            "Cloud Engineer",
            "DevOps Engineer",
            "Cloud Architect"
        ]
    }

    selected_path = st.selectbox(
        "Choose Career Field",
        list(career_paths.keys())
    )

    st.subheader(
        "🚀 Career Roadmap"
    )

    path = career_paths[
        selected_path
    ]

    for i, role in enumerate(path):

        st.success(
            f"Level {i+1}: {role}"
        )

        if i < len(path) - 1:
            st.markdown("⬇️")


# ==========================================
# SALARY EXPLORER
# ==========================================
elif menu == "Salary Explorer":

    st.header(
        "💰 Salary Explorer"
    )

    if (
        "job_title"
        in df_jobs.columns
    ):

        selected_job = st.selectbox(
            "Select Job Role",
            sorted(
                df_jobs[
                    "job_title"
                ]
                .dropna()
                .unique()
            )
        )

        salary_df = df_jobs[
            df_jobs[
                "job_title"
            ] == selected_job
        ]

        if (
            not salary_df.empty
            and
            "annual_salary_usd"
            in salary_df.columns
        ):

            avg_salary = (
                salary_df[
                    "annual_salary_usd"
                ].mean()
            )

            min_salary = (
                salary_df[
                    "annual_salary_usd"
                ].min()
            )

            max_salary = (
                salary_df[
                    "annual_salary_usd"
                ].max()
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Average Salary",
                    f"${avg_salary:,.0f}"
                )

            with col2:
                st.metric(
                    "Minimum Salary",
                    f"${min_salary:,.0f}"
                )

            with col3:
                st.metric(
                    "Maximum Salary",
                    f"${max_salary:,.0f}"
                )

            # COUNTRY ANALYSIS
            if (
                "country"
                in salary_df.columns
            ):

                country_salary = (
                    salary_df
                    .groupby("country")[
                        "annual_salary_usd"
                    ]
                    .mean()
                    .sort_values(
                        ascending=False
                    )
                    .reset_index()
                )

                st.subheader(
                    "🌍 Salary by Country"
                )

                fig = px.bar(
                    country_salary,
                    x="country",
                    y="annual_salary_usd",
                    title="Average Salary by Country"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


# ==========================================
# LEARNING RECOMMENDATION
# ==========================================
elif menu == "Learning Recommendation":

    st.header(
        "📚 Learning Recommendation"
    )

    learning_map = {

        "Data Scientist": [
            "Python",
            "Machine Learning",
            "Statistics",
            "SQL",
            "Data Visualization"
        ],

        "AI Engineer": [
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "Computer Vision",
            "NLP"
        ],

        "Software Engineer": [
            "Python",
            "Java",
            "Git",
            "Database",
            "Algorithms"
        ],

        "Cybersecurity Analyst": [
            "Networking",
            "Linux",
            "Ethical Hacking",
            "SIEM",
            "Security Tools"
        ],

        "Cloud Engineer": [
            "AWS",
            "Azure",
            "Docker",
            "Kubernetes",
            "Linux"
        ]
    }

    selected_career = st.selectbox(
        "Choose Career Goal",
        list(
            learning_map.keys()
        )
    )

    st.subheader(
        "🚀 Recommended Learning Path"
    )

    for i, skill in enumerate(
        learning_map[
            selected_career
        ]
    ):
        st.info(
            f"{i+1}. {skill}"
        )


# ==========================================
# FOOTER
# ==========================================
st.markdown("---")

st.caption(
    "🚀 FuturePath AI Dashboard "
    "| Developed by Data Science Team © 2026"
)
