import streamlit as st
import plotly.express as px

from models import CareerProfile
from services.career_analyzer import analyze_career
from services.chatbot import get_chat_response
from services.cv_parser import extract_text_from_file


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Career Navigator",
    page_icon="🧭",
    layout="wide",
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

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "Home",
    "Career Profile",
    "Career Assessment",
    "Skill Gap",
    "Career Roadmap",
    "AI Career Counselor",
]


def go_to(page_name: str):
    st.session_state.current_page = page_name
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧭 AI Career Navigator")

    current_index = pages.index(
        st.session_state.current_page
    )

    selected_page = st.radio(
        "Navigate",
        pages,
        index=current_index,
        key=f"navigation_{st.session_state.current_page}",
    )

    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    st.divider()

    st.caption(
        "MVP • Python + Streamlit + Gemini + ESCO"
    )


# ============================================================
# CURRENT PAGE
# ============================================================

page = st.session_state.current_page


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.title("🧭 AI Career Navigator")

    st.subheader(
        "Your AI-powered career planning assistant"
    )

    st.write(
        """
        Discover suitable career paths, identify your skill gaps,
        build a personalized roadmap, and get guidance from an
        AI career counselor.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 👤 Career Profile")
        st.write(
            "Tell us about your education, skills, interests, "
            "experience, and career goals."
        )

    with col2:
        st.markdown("### 📊 Career Assessment")
        st.write(
            "Analyze your profile and discover suitable career directions."
        )

    with col3:
        st.markdown("### 🚀 Career Roadmap")
        st.write(
            "Build a practical plan for improving your skills "
            "and reaching your goals."
        )

    st.divider()

    if st.button(
        "🚀 Start Assessment",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.profile = None
        st.session_state.assessment = None
        st.session_state.cv_text = ""
        st.session_state.chat_messages = []

        go_to("Career Profile")


# ============================================================
# CAREER PROFILE
# ============================================================

elif page == "Career Profile":

    st.title("👤 Career Profile")

    st.write(
        "Complete your profile so the AI can provide "
        "personalized career recommendations."
    )

    with st.form("career_profile_form"):

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
            placeholder=(
                "AI, renewable energy, data analysis, automation"
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

        uploaded_cv = st.file_uploader(
            "Upload CV (optional)",
            type=["pdf", "docx", "txt"],
        )

        submitted = st.form_submit_button(
            "💾 Save Profile & Continue",
            type="primary",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # FORM SUBMISSION
    # --------------------------------------------------------

    if submitted:

        # Basic validation
        if not degree.strip():
            st.error("Please enter your degree or field.")

        elif not skill_text.strip():
            st.error("Please enter at least one skill.")

        elif not interests.strip():
            st.error("Please enter your interests.")

        elif not career_goal.strip():
            st.error("Please enter your career goal.")

        else:

            # ------------------------------------------------
            # CV PROCESSING
            # ------------------------------------------------

            cv_text = ""

            if uploaded_cv is not None:

                try:

                    cv_text = extract_text_from_file(
                        uploaded_cv
                    )

                    st.session_state.cv_text = cv_text

                except Exception as e:

                    st.warning(
                        f"Could not process the CV: {e}"
                    )

            # ------------------------------------------------
            # CREATE PROFILE
            # ------------------------------------------------

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

                st.success(
                    "Profile saved successfully!"
                )

                go_to("Career Assessment")

            except Exception as e:

                st.error(
                    f"Could not save profile: {e}"
                )


# ============================================================
# CAREER ASSESSMENT
# ============================================================

elif page == "Career Assessment":

    st.title("📊 Career Assessment")

    if st.session_state.profile is None:

        st.warning(
            "Please complete your Career Profile first."
        )

        if st.button(
            "Go to Career Profile",
            type="primary",
        ):
            go_to("Career Profile")

    else:

        profile = st.session_state.profile

        st.write(
            "Analyze your profile to discover suitable career paths."
        )

        # ----------------------------------------------------
        # PROFILE PREVIEW
        # ----------------------------------------------------

        with st.expander(
            "View Your Profile",
            expanded=False,
        ):

            st.write(
                f"**Education:** {profile.education}"
            )

            st.write(
                f"**Degree / Field:** {profile.degree}"
            )

            st.write("**Skills:**")

            if profile.skills:

                for skill in profile.skills:

                    st.write(
                        f"- {skill.name}: {skill.level}%"
                    )

            else:

                st.write("No skills entered.")

            st.write(
                f"**Interests:** {', '.join(profile.interests)}"
            )

            st.write(
                "**Work Preferences:** "
                + (
                    ", ".join(profile.work_preferences)
                    if profile.work_preferences
                    else "None specified"
                )
            )

            st.write(
                f"**Experience:** {profile.experience}"
            )

            st.write(
                f"**Career Goal:** {profile.career_goal}"
            )

            if profile.cv_text:

                st.write(
                    "📄 CV information has been included."
                )

        st.divider()

        # ----------------------------------------------------
        # ANALYZE
        # ----------------------------------------------------

        if st.button(
            "🔍 Analyze My Career",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Analyzing your profile with AI and ESCO..."
            ):

                try:

                    assessment = analyze_career(
                        profile
                    )

                    st.session_state.assessment = assessment

                    st.success(
                        "Career assessment completed!"
                    )

                except Exception as e:

                    st.error(
                        f"Career analysis failed: {e}"
                    )

        # ----------------------------------------------------
        # SHOW ASSESSMENT
        # ----------------------------------------------------

        assessment = st.session_state.assessment

        if assessment is not None:

            st.divider()

            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            st.subheader("📝 Assessment Summary")

            st.write(
                assessment.summary
            )

            # ------------------------------------------------
            # STRENGTHS
            # ------------------------------------------------

            if assessment.strengths:

                st.subheader("💪 Your Strengths")

                for strength in assessment.strengths:

                    st.markdown(
                        f"- {strength}"
                    )

            # ------------------------------------------------
            # CAREER MATCHES
            # ------------------------------------------------

            st.subheader(
                "🎯 Recommended Career Paths"
            )

            if not assessment.matches:

                st.info(
                    "No career matches were returned."
                )

            else:

                for index, match in enumerate(
                    assessment.matches,
                    start=1,
                ):

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### {index}. {match.career_title}"
                        )

                        st.metric(
                            "Match Score",
                            f"{match.match_score}%",
                        )

                        st.write(
                            match.reason
                        )

                        if match.required_skills:

                            st.markdown(
                                "**Required Skills**"
                            )

                            st.write(
                                ", ".join(
                                    match.required_skills
                                )
                            )

                        if match.missing_skills:

                            st.markdown(
                                "**Missing Skills**"
                            )

                            st.write(
                                ", ".join(
                                    match.missing_skills
                                )
                            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "🧩 View Skill Gap",
                    type="primary",
                    use_container_width=True,
                ):
                    go_to("Skill Gap")

            with col2:

                if st.button(
                    "🗺️ View Career Roadmap",
                    use_container_width=True,
                ):
                    go_to("Career Roadmap")


# ============================================================
# SKILL GAP
# ============================================================

elif page == "Skill Gap":

    st.title("🧩 Skill Gap Analysis")

    if st.session_state.profile is None:

        st.warning(
            "Please complete your Career Profile first."
        )

        if st.button(
            "Go to Career Profile",
            type="primary",
        ):
            go_to("Career Profile")

    elif st.session_state.assessment is None:

        st.warning(
            "Please complete your Career Assessment first."
        )

        if st.button(
            "Go to Career Assessment",
            type="primary",
        ):
            go_to("Career Assessment")

    else:

        assessment = st.session_state.assessment

        st.write(
            "Compare your current skills with the skills "
            "required for your recommended careers."
        )

        # ----------------------------------------------------
        # CAREER SELECTION
        # ----------------------------------------------------

        if not assessment.matches:

            st.info(
                "No career matches are available."
            )

        else:

            career_names = [
                match.career_title
                for match in assessment.matches
            ]

            selected_career = st.selectbox(
                "Select a career",
                career_names,
            )

            selected_match = next(
                match
                for match in assessment.matches
                if match.career_title == selected_career
            )

            # ------------------------------------------------
            # SKILL GAP DATA
            # ------------------------------------------------

            st.subheader(
                f"🛠️ Skill Gaps for {selected_match.career_title}"
            )

            if selected_match.skill_gaps:

                gap_rows = []

                for gap in selected_match.skill_gaps:

                    gap_rows.append(
                        {
                            "Skill": gap.skill,
                            "Current Level": gap.current_level,
                            "Required Level": gap.required_level,
                            "Gap": gap.gap_score,
                        }
                    )

                # Plotly chart
                fig = px.bar(
                    gap_rows,
                    x="Skill",
                    y=["Current Level", "Required Level"],
                    barmode="group",
                    title="Current vs Required Skill Level",
                    range_y=[0, 100],
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                # Detailed table
                st.subheader(
                    "📋 Skill Gap Details"
                )

                for gap in selected_match.skill_gaps:

                    st.markdown(
                        f"### {gap.skill}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Current",
                            f"{gap.current_level}%",
                        )

                    with col2:
                        st.metric(
                            "Required",
                            f"{gap.required_level}%",
                        )

                    with col3:
                        st.metric(
                            "Gap",
                            f"{gap.gap_score}%",
                        )

            else:

                st.info(
                    "No skill-gap details were returned."
                )

            # ------------------------------------------------
            # MISSING SKILLS
            # ------------------------------------------------

            if selected_match.missing_skills:

                st.subheader(
                    "📚 Skills to Develop"
                )

                for skill in selected_match.missing_skills:

                    st.markdown(
                        f"- {skill}"
                    )

        st.divider()

        if st.button(
            "🗺️ Continue to Career Roadmap",
            type="primary",
            use_container_width=True,
        ):
            go_to("Career Roadmap")


# ============================================================
# CAREER ROADMAP
# ============================================================

elif page == "Career Roadmap":

    st.title("🗺️ Career Roadmap")

    if st.session_state.profile is None:

        st.warning(
            "Please complete your Career Profile first."
        )

        if st.button(
            "Go to Career Profile",
            type="primary",
        ):
            go_to("Career Profile")

    elif st.session_state.assessment is None:

        st.warning(
            "Please complete your Career Assessment first."
        )

        if st.button(
            "Go to Career Assessment",
            type="primary",
        ):
            go_to("Career Assessment")

    else:

        assessment = st.session_state.assessment

        st.write(
            "Follow the roadmap to move toward your target career."
        )

        # ----------------------------------------------------
        # CAREER SELECTION
        # ----------------------------------------------------

        if not assessment.matches:

            st.info(
                "No career matches are available."
            )

        else:

            career_names = [
                match.career_title
                for match in assessment.matches
            ]

            selected_career = st.selectbox(
                "Select a career roadmap",
                career_names,
            )

            selected_match = next(
                match
                for match in assessment.matches
                if match.career_title == selected_career
            )

            # ------------------------------------------------
            # ROADMAP
            # ------------------------------------------------

            st.subheader(
                f"🚀 Roadmap for {selected_match.career_title}"
            )

            roadmap = selected_match.learning_roadmap

            if roadmap:

                for index, item in enumerate(
                    roadmap,
                    start=1,
                ):

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### Phase {index}: {item.phase}"
                        )

                        st.caption(
                            f"⏱️ {item.timeframe}"
                        )

                        st.write(
                            item.objective
                        )

                        if item.topics:

                            st.markdown(
                                "**Topics to Learn**"
                            )

                            for topic in item.topics:

                                st.markdown(
                                    f"- {topic}"
                                )

                        st.markdown(
                            f"**Deliverable:** {item.deliverable}"
                        )

            else:

                st.info(
                    "No learning roadmap was returned."
                )

            # ------------------------------------------------
            # PROJECTS
            # ------------------------------------------------

            if selected_match.recommended_projects:

                st.divider()

                st.subheader(
                    "💻 Recommended Projects"
                )

                for project in selected_match.recommended_projects:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### {project.title}"
                        )

                        st.write(
                            project.description
                        )

                        if project.skills:

                            st.write(
                                "**Skills practiced:** "
                                + ", ".join(project.skills)
                            )

            # ------------------------------------------------
            # NEXT STEPS
            # ------------------------------------------------

            if selected_match.next_steps:

                st.divider()

                st.subheader(
                    "✅ Next Steps"
                )

                for step in selected_match.next_steps:

                    st.markdown(
                        f"- {step}"
                    )

        st.divider()

        if st.button(
            "🤖 Talk to AI Career Counselor",
            type="primary",
            use_container_width=True,
        ):
            go_to("AI Career Counselor")


# ============================================================
# AI CAREER COUNSELOR
# ============================================================

elif page == "AI Career Counselor":

    st.title("🤖 AI Career Counselor")

    if st.session_state.profile is None:

        st.warning(
            "Please complete your Career Profile first."
        )

        if st.button(
            "Go to Career Profile",
            type="primary",
        ):
            go_to("Career Profile")

    else:

        st.write(
            "Ask the AI counselor questions about your career."
        )

        st.divider()

        # ----------------------------------------------------
        # EXPERIENCE LEVEL
        # ----------------------------------------------------

        experience_level = st.radio(
            "Choose your guidance level:",
            [
                "Beginner",
                "Intermediate",
                "Expert",
            ],
            horizontal=True,
        )

        level_descriptions = {
            "Beginner":
                "Simple explanations with step-by-step guidance.",

            "Intermediate":
                "More technical and practical guidance.",

            "Expert":
                "Advanced career and technical guidance.",
        }

        st.caption(
            level_descriptions[experience_level]
        )

        # ----------------------------------------------------
        # QUICK QUESTIONS
        # ----------------------------------------------------

        quick_question = st.selectbox(
            "Quick question",
            [
                "Select a question...",
                "What career should I choose?",
                "What skills should I learn?",
                "How can I get my first job?",
                "How should I build my portfolio?",
                "How can I prepare for interviews?",
            ],
        )

        if st.button(
            "💡 Get Guidance",
            type="primary",
        ):

            if quick_question != "Select a question...":

                user_message = quick_question

                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content": user_message,
                    }
                )

                try:

                    response = get_chat_response(
                        profile=st.session_state.profile,
                        message=user_message,
                        conversation=st.session_state.chat_messages,
                        experience_level=experience_level,
                    )

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                        }
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not get AI guidance: {e}"
                    )

        # ----------------------------------------------------
        # DISPLAY CHAT HISTORY
        # ----------------------------------------------------

        for message in st.session_state.chat_messages:

            with st.chat_message(
                message["role"]
            ):

                st.write(
                    message["content"]
                )

        # ----------------------------------------------------
        # CHAT INPUT
        # ----------------------------------------------------

        user_prompt = st.chat_input(
            "Ask your career question..."
        )

        if user_prompt:

            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": user_prompt,
                }
            )

            with st.chat_message("user"):

                st.write(
                    user_prompt
                )

            try:

                response = get_chat_response(
                    profile=st.session_state.profile,
                    message=user_prompt,
                    conversation=st.session_state.chat_messages,
                    experience_level=experience_level,
                )

                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                with st.chat_message(
                    "assistant"
                ):

                    st.write(
                        response
                    )

            except Exception as e:

                st.error(
                    f"Could not get AI response: {e}"
                )
