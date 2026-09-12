```python
import streamlit as st
import plotly.express as px

from models import CareerProfile
from services.cv_parser import extract_cv_text
from services.career_analyzer import analyze_career
from services.chatbot import chat_with_counselor
from services.esco_client import ESCOClient
from config import get_settings


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Career Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SETTINGS
# ============================================================

settings = get_settings()
esco = ESCOClient(settings.esco_base_url)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: .2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    .card {
        padding: 1rem 1.2rem;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        background: #ffffff;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "profile" not in st.session_state:
    st.session_state.profile = None

if "assessment" not in st.session_state:
    st.session_state.assessment = None

if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# THIS CONTROLS WHICH PAGE IS DISPLAYED
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


# ============================================================
# PAGE LIST
# ============================================================

pages = [
    "Home",
    "Career Profile",
    "Career Assessment",
    "Skill Gap",
    "Career Roadmap",
    "AI Career Counselor",
]


# ============================================================
# NAVIGATION FUNCTION
# ============================================================

def go_to(page_name):
    """
    Change the current page and refresh Streamlit.
    """
    st.session_state.current_page = page_name
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧭 AI Career Navigator")

    # Find current page index
    current_index = pages.index(st.session_state.current_page)

    selected_page = st.radio(
        "Navigate",
        pages,
        index=current_index,
        key="navigation_radio",
    )

    # If user manually clicks a page in sidebar
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    st.divider()

    st.caption("MVP • Python + Streamlit + Gemini + ESCO")


# ============================================================
# HELPER
# ============================================================

def require_profile():

    if not st.session_state.profile:

        st.warning(
            "Please complete the Career Profile first."
        )

        if st.button(
            "👤 Go to Career Profile",
            type="primary",
        ):
            go_to("Career Profile")

        return False

    return True


def require_assessment():

    if not st.session_state.assessment:

        st.warning(
            "Please complete the Career Assessment first."
        )

        if st.button(
            "🎯 Go to Career Assessment",
            type="primary",
        ):
            go_to("Career Assessment")

        return False

    return True


# ============================================================
# CURRENT PAGE
# ============================================================

page = st.session_state.current_page


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.markdown(
        '<div class="main-title">🧭 AI Career Navigator</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "A personalized AI career counselor that turns your "
        "education, skills, interests and goals into practical "
        "career options and a learning plan."
        "</div>",
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
        4. ESCO provides occupation and skill context.
        5. Review career matches.
        6. Review skill gaps and roadmap.
        7. Chat with the AI Career Counselor.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # FIXED START BUTTON
    # --------------------------------------------------------

    if st.button(
        "🚀 Start Assessment",
        type="primary",
        use_container_width=True,
    ):

        # Start a NEW assessment
        st.session_state.profile = None
        st.session_state.assessment = None
        st.session_state.cv_text = ""
        st.session_state.chat_messages = []

        # MOVE TO CAREER PROFILE
        go_to("Career Profile")

    st.info(
        "Start by creating your Career Profile. "
        "The CV upload is optional."
    )


# ============================================================
# CAREER PROFILE
# ============================================================

elif page == "Career Profile":

    st.header("👤 Career Profile")

    st.write(
        "Tell the navigator about your education, skills, "
        "interests and career goals."
    )

    with st.form("profile_form"):

        education = st.selectbox(
            "Education level",
            [
                "High School",
                "Diploma",
                "Bachelor's",
                "Master's",
                "PhD",
                "Other",
            ],
        )

        degree = st.text_input(
            "Degree / field",
            placeholder="e.g., Computer Science",
        )

        st.subheader("Skills")

        skill_text = st.text_area(
            "Skills and approximate levels",
            placeholder=(
                "Python: intermediate\n"
                "SQL: beginner\n"
                "Machine Learning: beginner"
            ),
            height=130,
        )

        interests = st.text_area(
            "Interests",
            placeholder=(
                "AI, data analysis, machine learning, automation"
            ),
        )

        work_preferences = st.multiselect(
            "Work preferences",
            [
                "Remote",
                "Hybrid",
                "On-site",
                "Individual contributor",
                "Team-based",
                "Technical",
                "Management",
                "Research",
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
            placeholder=(
                "What do you want to achieve in the next 1–3 years?"
            ),
            height=100,
        )

        cv_file = st.file_uploader(
            "Optional CV upload",
            type=["pdf", "docx"],
        )

        submitted = st.form_submit_button(
            "💾 Save Profile & Continue",
            type="primary",
        )

    # --------------------------------------------------------
    # SAVE PROFILE
    # --------------------------------------------------------

    if submitted:

        if (
            not degree.strip()
            or not skill_text.strip()
            or not career_goal.strip()
        ):

            st.error(
                "Please provide at least your degree/field, "
                "skills and career goal."
            )

        else:

            cv_text = ""

            if cv_file:

                try:

                    cv_text = extract_cv_text(
                        cv_file.getvalue(),
                        cv_file.name,
                    )

                    st.session_state.cv_text = cv_text

                except Exception as exc:

                    st.error(
                        f"Could not read the CV: {exc}"
                    )

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

            st.success(
                "Profile saved successfully!"
            )

            # ------------------------------------------------
            # FIX:
            # MOVE TO CAREER ASSESSMENT
            # ------------------------------------------------

            go_to("Career Assessment")


# ============================================================
# CAREER ASSESSMENT
# ============================================================

elif page == "Career Assessment":

    st.header("🎯 Career Assessment")

    if require_profile():

        profile = st.session_state.profile

        st.write(
            "Your profile is ready. Let Gemini analyze "
            "your best career options."
        )

        st.divider()

        # ----------------------------------------------------
        # ANALYZE BUTTON
        # ----------------------------------------------------

        if st.button(
            "🧠 Analyze My Career Options",
            type="primary",
            use_container_width=True,
        ):

            if not settings.gemini_api_key:

                st.error(
                    "Gemini API key is missing. "
                    "Please add GEMINI_API_KEY to your "
                    "environment or Streamlit Secrets."
                )

            else:

                with st.spinner(
                    "Analyzing your career profile..."
                ):

                    try:

                        assessment = analyze_career(
                            profile=profile,
                            gemini_api_key=settings.gemini_api_key,
                            model=settings.gemini_model,
                            esco_client=esco,
                        )

                        st.session_state.assessment = assessment

                        st.success(
                            "Career assessment completed!"
                        )

                    except Exception as exc:

                        st.error(
                            f"Assessment failed: {exc}"
                        )

        # ----------------------------------------------------
        # SHOW RESULTS
        # ----------------------------------------------------

        assessment = st.session_state.assessment

        if assessment:

            st.success(
                "Your career recommendations are ready."
            )

            st.subheader("🎯 Top Career Matches")

            for match in assessment.matches:

                with st.container(border=True):

                    c1, c2 = st.columns([4, 1])

                    with c1:

                        st.markdown(
                            f"### {match.career_title}"
                        )

                        st.write(
                            match.reason
                        )

                    with c2:

                        st.metric(
                            "Match",
                            f"{match.match_score}%",
                        )

                    if match.esco_context:

                        st.caption(
                            f"ESCO context: "
                            f"{match.esco_context}"
                        )

                    st.write(
                        "**Required skills:** "
                        + ", ".join(
                            match.required_skills
                        )
                    )

            st.subheader("💪 Your Strengths")

            st.write(
                " • ".join(
                    assessment.strengths
                )
            )

            st.subheader("💡 Overall Guidance")

            st.write(
                assessment.summary
            )

            st.divider()

            # ------------------------------------------------
            # NEXT PAGE BUTTONS
            # ------------------------------------------------

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "📊 Continue to Skill Gap",
                    use_container_width=True,
                ):

                    go_to("Skill Gap")

            with c2:

                if st.button(
                    "🛣️ Continue to Career Roadmap",
                    use_container_width=True,
                ):

                    go_to("Career Roadmap")


# ============================================================
# SKILL GAP
# ============================================================

elif page == "Skill Gap":

    st.header("📊 Skill Gap Analysis")

    if require_profile() and require_assessment():

        assessment = st.session_state.assessment

        selected = st.selectbox(
            "Choose a target career",
            [
                m.career_title
                for m in assessment.matches
            ],
        )

        match = next(
            m for m in assessment.matches
            if m.career_title == selected
        )

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

            fig.update_layout(
                yaxis_title="Gap (%)",
                xaxis_title="",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            for gap in match.skill_gaps:

                st.progress(
                    max(
                        0,
                        min(
                            100,
                            gap.current_level,
                        ),
                    ),
                    text=(
                        f"{gap.skill}: "
                        f"current {gap.current_level}% • "
                        f"required {gap.required_level}%"
                    ),
                )

        else:

            st.info(
                "No detailed skill gaps were returned."
            )

        st.subheader("Missing / Weak Skills")

        for skill in match.missing_skills:

            st.write(f"- {skill}")

        st.divider()

        if st.button(
            "🛣️ Continue to Career Roadmap",
            type="primary",
            use_container_width=True,
        ):

            go_to("Career Roadmap")


# ============================================================
# CAREER ROADMAP
# ============================================================

elif page == "Career Roadmap":

    st.header("🛣️ Career Roadmap")

    if require_profile() and require_assessment():

        assessment = st.session_state.assessment

        selected = st.selectbox(
            "Choose a target career",
            [
                m.career_title
                for m in assessment.matches
            ],
            key="roadmap_career",
        )

        match = next(
            m for m in assessment.matches
            if m.career_title == selected
        )

        st.subheader("📚 Learning Roadmap")

        for item in match.learning_roadmap:

            with st.container(border=True):

                st.markdown(
                    f"**{item.phase} — "
                    f"{item.timeframe}**"
                )

                st.write(
                    item.objective
                )

                st.write(
                    "**Topics:** "
                    + ", ".join(item.topics)
                )

                st.write(
                    "**Deliverable:** "
                    + item.deliverable
                )

        st.subheader("🚀 Recommended Projects")

        for project in match.recommended_projects:

            st.markdown(
                f"**{project.title}**"
            )

            st.write(
                project.description
            )

            st.caption(
                "Skills: "
                + ", ".join(project.skills)
            )

        st.subheader("✅ Next Steps")

        for step in match.next_steps:

            st.write(
                f"☐ {step}"
            )

        st.divider()

        if st.button(
            "🤖 Continue to AI Career Counselor",
            type="primary",
            use_container_width=True,
        ):

            go_to("AI Career Counselor")


# ============================================================
# AI CAREER COUNSELOR
# ============================================================

elif page == "AI Career Counselor":

    st.header("🤖 AI Career Counselor")

    if require_profile():

        level = st.radio(
            "Explanation level",
            [
                "Beginner",
                "Intermediate",
                "Expert",
            ],
            horizontal=True,
        )

        if st.session_state.assessment:

            st.caption(
                "The counselor uses your profile and "
                "career assessment as context."
            )

        else:

            st.caption(
                "Complete a career assessment for richer answers."
            )

        # ----------------------------------------------------
        # QUICK QUESTIONS
        # ----------------------------------------------------

        st.subheader("💬 Quick Questions")

        quick_question = st.selectbox(
            "Choose a question",
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
        ):

            if not settings.gemini_api_key:

                st.error(
                    "Gemini API key is missing."
                )

            else:

                with st.chat_message("user"):

                    st.markdown(
                        quick_question
                    )

                with st.chat_message("assistant"):

                    with st.spinner(
                        "Thinking..."
                    ):

                        try:

                            answer = chat_with_counselor(
                                question=quick_question,
                                profile=st.session_state.profile,
                                assessment=st.session_state.assessment,
                                level=level,
                                api_key=settings.gemini_api_key,
                                model=settings.gemini_model,
                            )

                            st.markdown(answer)

                        except Exception as exc:

                            st.error(
                                f"Counselor error: {exc}"
                            )

        st.divider()

        # ----------------------------------------------------
        # CHAT HISTORY
        # ----------------------------------------------------

        for msg in st.session_state.chat_messages:

            with st.chat_message(
                msg["role"]
            ):

                st.markdown(
                    msg["content"]
                )

        # ----------------------------------------------------
        # NORMAL CHAT
        # ----------------------------------------------------

        prompt = st.chat_input(
            "Ask about careers, skills, learning or your roadmap..."
        )

        if prompt:

            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            with st.chat_message("user"):

                st.markdown(prompt)

            if not settings.gemini_api_key:

                answer = (
                    "Gemini API key is missing. "
                    "Please configure GEMINI_API_KEY."
                )

            else:

                with st.chat_message("assistant"):

                    with st.spinner(
                        "Thinking..."
                    ):

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

                            answer = (
                                f"Chatbot error: {exc}"
                            )

                    st.markdown(answer)

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )
```
