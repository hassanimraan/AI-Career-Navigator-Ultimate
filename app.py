import streamlit as st
import plotly.express as px

from models import CareerProfile
from services.cv_parser import extract_cv_text
from services.career_analyzer import analyze_career
from services.chatbot import chat_with_counselor
from services.esco_client import ESCOClient
from config import get_settings

st.set_page_config(
    page_title="AI Career Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

settings = get_settings()
esco = ESCOClient(settings.esco_base_url)

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "page": "Home",
    "profile": None,
    "assessment": None,
    "cv_text": "",
    "chat_messages": [],
    "counselor_level": "Beginner",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Small helpers
# -----------------------------
PAGES = [
    "Home",
    "Career Profile",
    "Career Assessment",
    "Skill Gap",
    "Career Roadmap",
    "AI Career Counselor",
]

def go_to(page: str):
    st.session_state.page = page
    st.rerun()

def require_profile():
    if not st.session_state.profile:
        st.warning("Please complete the Career Profile first.")
        if st.button("Go to Career Profile", type="primary"):
            go_to("Career Profile")
        return False
    return True

def require_assessment():
    if not st.session_state.assessment:
        st.info("Run Career Assessment first.")
        if st.button("Go to Career Assessment", type="primary"):
            go_to("Career Assessment")
        return False
    return True

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {font-size: 2.6rem; font-weight: 800; margin-bottom: .2rem;}
    .subtitle {font-size: 1.05rem; color: #64748b; margin-bottom: 1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.title("🧭 AI Career Navigator")

    selected_page = st.radio(
        "Navigate",
        PAGES,
        index=PAGES.index(st.session_state.page),
        key="navigation_radio",
    )
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.divider()

    profile_status = "✅ Profile ready" if st.session_state.profile else "⬜ Profile not created"
    assessment_status = "✅ Assessment ready" if st.session_state.assessment else "⬜ Assessment not run"
    st.caption(profile_status)
    st.caption(assessment_status)

    with st.expander("System status"):
        st.write(f"Gemini model: `{settings.gemini_model}`")
        if settings.gemini_api_key:
            st.success("Gemini API key detected.")
        else:
            st.error("Gemini API key is missing.")
        st.write(f"ESCO: `{settings.esco_base_url}`")

    if st.button("🔄 Start over", use_container_width=True):
        for key in ["profile", "assessment", "cv_text"]:
            st.session_state[key] = defaults[key]
        st.session_state.chat_messages = []
        st.session_state.counselor_level = "Beginner"
        go_to("Career Profile")

page = st.session_state.page

# -----------------------------
# Home
# -----------------------------
if page == "Home":
    st.markdown('<div class="main-title">🧭 AI Career Navigator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A personalized AI career counselor that turns your '
        'education, skills, interests and goals into practical career options and a learning plan.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Career Matches", "3–5")
    with c2:
        st.metric("AI Engine", "Gemini")
    with c3:
        st.metric("Knowledge Source", "ESCO")

    st.markdown("### How it works")
    st.markdown(
        """
        1. Build your career profile.
        2. Optionally upload your CV.
        3. Gemini analyzes your profile.
        4. ESCO provides occupation context where available.
        5. Review career matches, skill gaps, roadmap and projects.
        6. Ask the AI Career Counselor questions at Beginner, Intermediate or Expert level.
        """
    )

    if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
        # The old version reset the profile but stayed on Home, which made this
        # button appear to do nothing. Now it explicitly navigates to the form.
        st.session_state.profile = None
        st.session_state.assessment = None
        st.session_state.chat_messages = []
        go_to("Career Profile")

    if st.session_state.profile:
        st.success("Your profile is already loaded.")
        if st.button("Continue to Career Assessment", use_container_width=True):
            go_to("Career Assessment")

# -----------------------------
# Career Profile
# -----------------------------
elif page == "Career Profile":
    st.header("👤 Career Profile")
    st.write("Tell the navigator about your education, skills, interests and career goals.")

    with st.form("profile_form"):
        education = st.selectbox(
            "Education level",
            ["High School", "Diploma", "Bachelor's", "Master's", "PhD", "Other"],
        )
        degree = st.text_input(
            "Degree / field",
            placeholder="e.g., Electrical Engineering",
        )

        st.subheader("Skills")
        skill_text = st.text_area(
            "Skills and approximate levels",
            placeholder=(
                "Python: intermediate\n"
                "Electrical design: advanced\n"
                "Project management: beginner"
            ),
            height=130,
        )

        interests = st.text_area(
            "Interests",
            placeholder="AI, renewable energy, data analysis, automation",
        )

        work_preferences = st.multiselect(
            "Work preferences",
            [
                "Remote", "Hybrid", "On-site", "Individual contributor",
                "Team-based", "Technical", "Management", "Research",
                "Entrepreneurship",
            ],
        )

        experience = st.text_area(
            "Experience / projects",
            placeholder=(
                "Describe internships, jobs, university projects, "
                "freelance work, certifications, etc."
            ),
            height=150,
        )

        career_goal = st.text_area(
            "Career goal",
            placeholder="What do you want to achieve in the next 1–3 years?",
            height=100,
        )

        cv_file = st.file_uploader(
            "Optional CV upload",
            type=["pdf", "docx"],
            help="The MVP extracts CV text locally.",
        )

        submitted = st.form_submit_button(
            "💾 Save Profile & Continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not degree.strip() or not skill_text.strip() or not career_goal.strip():
            st.error("Please provide at least your degree/field, skills and career goal.")
        else:
            cv_text = ""
            if cv_file:
                try:
                    cv_text = extract_cv_text(cv_file.getvalue(), cv_file.name)
                    st.session_state.cv_text = cv_text
                except Exception as exc:
                    st.error(f"Could not read the CV: {exc}")
                    cv_text = ""

            try:
                profile = CareerProfile.from_form(
                    education=education,
                    degree=degree,
                    skill_text=skill_text,
                    interests=interests,
                    work_preferences=work_preferences,
                    experience=experience,
                    career_goal=career_goal,
                    cv_text=cv_text,
                )
                st.session_state.profile = profile
                st.session_state.assessment = None
                st.session_state.chat_messages = []
                st.success("Profile saved successfully.")
                go_to("Career Assessment")
            except Exception as exc:
                st.error(f"Could not save the profile: {exc}")

    if st.session_state.profile:
        st.divider()
        st.success("A profile is already loaded in this session.")
        with st.expander("View current profile"):
            st.json(st.session_state.profile.model_dump())

# -----------------------------
# Career Assessment
# -----------------------------
elif page == "Career Assessment":
    st.header("🎯 Career Assessment")

    if require_profile():
        if not settings.gemini_api_key:
            st.error(
                "Gemini API key is missing. Add GEMINI_API_KEY to your local .env "
                "or Streamlit Cloud Secrets."
            )
        else:
            st.caption(
                f"AI model: `{settings.gemini_model}`. "
                "Click the button below to generate your personalized assessment."
            )

            if st.button(
                "🧠 Analyze My Career Options",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(
                    "Analyzing your profile and checking ESCO occupation context..."
                ):
                    try:
                        st.session_state.assessment = analyze_career(
                            profile=st.session_state.profile,
                            gemini_api_key=settings.gemini_api_key,
                            model=settings.gemini_model,
                            esco_client=esco,
                        )
                        st.success("Assessment completed successfully.")
                    except Exception as exc:
                        st.session_state.assessment = None
                        st.error(f"Assessment failed: {exc}")
                        st.info(
                            "Open the Streamlit Cloud logs if this is deployed. "
                            "The most common causes are an invalid Gemini key, "
                            "an unavailable model name, or a dependency error."
                        )

        assessment = st.session_state.assessment
        if assessment:
            st.success("Assessment is ready.")
            st.subheader("Top Career Matches")

            for match in assessment.matches:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"### {match.career_title}")
                        st.write(match.reason)
                    with c2:
                        st.metric("Match", f"{match.match_score}%")
                    if match.esco_context:
                        st.caption(f"ESCO context: {match.esco_context}")
                    if match.required_skills:
                        st.write("**Required skills:** " + ", ".join(match.required_skills))

            st.subheader("Your Strengths")
            st.write(" • ".join(assessment.strengths))

            st.subheader("Overall Guidance")
            st.write(assessment.summary)

            if st.button("Continue to Skill Gap", use_container_width=True):
                go_to("Skill Gap")

# -----------------------------
# Skill Gap
# -----------------------------
elif page == "Skill Gap":
    st.header("📊 Skill Gap Analysis")

    if require_profile() and require_assessment():
        assessment = st.session_state.assessment
        titles = [m.career_title for m in assessment.matches]

        if not titles:
            st.warning("The assessment returned no career matches. Run the assessment again.")
        else:
            selected = st.selectbox("Choose a target career", titles)
            match = next(m for m in assessment.matches if m.career_title == selected)

            gap_rows = [
                {
                    "Skill": g.skill,
                    "Current": g.current_level,
                    "Required": g.required_level,
                    "Gap": g.gap_score,
                }
                for g in match.skill_gaps
            ]

            if gap_rows:
                fig = px.bar(
                    gap_rows,
                    x="Skill",
                    y="Gap",
                    title=f"Skill Gap — {selected}",
                    range_y=[0, 100],
                )
                fig.update_layout(yaxis_title="Gap (%)", xaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

                for gap in match.skill_gaps:
                    st.progress(
                        max(0, min(100, gap.current_level)),
                        text=(
                            f"{gap.skill}: current {gap.current_level}% • "
                            f"required {gap.required_level}%"
                        ),
                    )
            else:
                st.info("No detailed skill gaps were returned for this career.")

            st.subheader("Missing / Weak Skills")
            if match.missing_skills:
                for skill in match.missing_skills:
                    st.write(f"- {skill}")
            else:
                st.write("No missing skills were identified.")

            st.caption(
                "Scores are AI-estimated guidance, not formal aptitude or hiring assessments."
            )

# -----------------------------
# Career Roadmap
# -----------------------------
elif page == "Career Roadmap":
    st.header("🛣️ Career Roadmap")

    if require_profile() and require_assessment():
        assessment = st.session_state.assessment
        titles = [m.career_title for m in assessment.matches]

        if not titles:
            st.warning("No career matches are available. Run the assessment again.")
        else:
            selected = st.selectbox(
                "Choose a target career",
                titles,
                key="roadmap_career",
            )
            match = next(m for m in assessment.matches if m.career_title == selected)

            st.subheader("Learning Roadmap")
            for item in match.learning_roadmap:
                with st.container(border=True):
                    st.markdown(f"**{item.phase} — {item.timeframe}**")
                    st.write(item.objective)
                    st.write("**Topics:** " + ", ".join(item.topics))
                    st.write("**Deliverable:** " + item.deliverable)

            st.subheader("Recommended Projects")
            for project in match.recommended_projects:
                st.markdown(f"**{project.title}**")
                st.write(project.description)
                st.caption("Skills: " + ", ".join(project.skills))

            st.subheader("Next Steps")
            for step in match.next_steps:
                st.write(f"☐ {step}")

# -----------------------------
# AI Career Counselor
# -----------------------------
elif page == "AI Career Counselor":
    st.header("🤖 AI Career Counselor")

    if require_profile():
        level = st.radio(
            "Explanation level",
            ["Beginner", "Intermediate", "Expert"],
            horizontal=True,
            index=["Beginner", "Intermediate", "Expert"].index(
                st.session_state.counselor_level
            ),
        )
        st.session_state.counselor_level = level

        st.caption(
            {
                "Beginner": "Simple language, definitions and concrete examples.",
                "Intermediate": "Practical detail with moderate technical depth.",
                "Expert": "Concise, technical and strategic.",
            }[level]
        )

        if st.session_state.assessment:
            st.success("Your latest career assessment is available to the counselor.")
        else:
            st.info(
                "You can ask questions now. For more personalized answers, "
                "run Career Assessment first."
            )

        # This fixes the original UX problem: selecting Beginner/Intermediate/Expert
        # alone never generated an answer. The user now has a clear action.
        starter_question = st.selectbox(
            "Choose a quick question",
            [
                "What career should I focus on first?",
                "What are my biggest skill gaps?",
                "What should I learn in the next 30 days?",
                "What portfolio project should I build?",
                "How can I improve my chances of getting hired?",
            ],
        )

        if st.button(
            f"✨ Get {level} Guidance",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.chat_messages.append(
                {"role": "user", "content": starter_question}
            )

            if not settings.gemini_api_key:
                answer = (
                    "Gemini API key is missing. Add GEMINI_API_KEY to "
                    "Streamlit Secrets or your local .env file."
                )
            else:
                with st.spinner("Thinking..."):
                    try:
                        answer = chat_with_counselor(
                            question=starter_question,
                            profile=st.session_state.profile,
                            assessment=st.session_state.assessment,
                            level=level,
                            api_key=settings.gemini_api_key,
                            model=settings.gemini_model,
                        )
                    except Exception as exc:
                        answer = f"Chatbot error: {exc}"

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input(
            "Ask a custom question about careers, skills, learning or your roadmap..."
        )
        if prompt:
            st.session_state.chat_messages.append(
                {"role": "user", "content": prompt}
            )

            if not settings.gemini_api_key:
                answer = (
                    "Gemini API key is missing. Add GEMINI_API_KEY to "
                    "Streamlit Secrets or your local .env file."
                )
            else:
                with st.spinner("Thinking..."):
                    try:
                        answer = chat_with_counselor(
                            question=prompt,
                            profile=st.session_state.profile,
                            assessment=st.session_state.assessment,
                            level=level,
                            api_key=settings.gemini_api_key,
                            model=settings.gemini_model,
                        )
                    except Exception as exc:
                        answer = f"Chatbot error: {exc}"

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()
