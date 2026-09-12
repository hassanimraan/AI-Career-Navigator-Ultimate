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


def go_to(page_name):
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

    # IMPORTANT:
    # Dynamic key prevents the sidebar radio from
    # overwriting button-based navigation.
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
            "Tell us about your education, experience, interests, and goals."
        )

    with col2:
        st.markdown("### 📊 Career Assessment")
        st.write(
            "Analyze your profile and discover suitable career directions."
        )

    with col3:
        st.markdown("### 🚀 Career Roadmap")
        st.write(
            "Build a practical plan for improving your skills and reaching your goals."
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
        "Complete your profile so the AI can provide personalized career recommendations."
    )

    with st.form("career_profile_form"):

      education = st.selectbox(
            "Education level",
            ["High School", "Diploma", "Bachelor's", "Master's", "PhD", "Other"],
        )
       
        degree = st.text_input("Degree / field", placeholder="e.g., Electrical Engineering")
        
        st.subheader("Skills")
        skill_text = st.text_area(
            "Skills and approximate levels",
            placeholder="Python: intermediate\nElectrical design: advanced\nProject management: beginner",
            height=130,
        )

        interests = st.text_area(
            "Interests",
            placeholder="AI, renewable energy, data analysis, automation",
        )

        work_preferences = st.multiselect(
            "Work preferences",
            ["Remote", "Hybrid", "On-site", "Individual contributor",
             "Team-based", "Technical", "Management", "Research", "Entrepreneurship"],
        )

        experience = st.text_area(
            "Experience / projects",
            placeholder="Describe internships, jobs, university projects, freelance work, certifications, etc.",
            height=150,
        )

        career_goal = st.text_area(
            "Career goal",
            placeholder="What do you want to achieve in the next 1–3 years?",
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

    if submitted:

        if not name.strip():
            st.error("Please enter your name.")

        elif not education.strip():
            st.error("Please enter your education.")

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
                    name=name,
                    education=education,
                    experience=experience,
                    skills=skills,
                    interests=interests,
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

        st.write(
            "Analyze your profile to discover suitable career paths."
        )

        profile = st.session_state.profile

        with st.expander(
            "View Your Profile",
            expanded=False,
        ):

            st.write(
                f"**Name:** {getattr(profile, 'name', '')}"
            )

            st.write(
                f"**Education:** {getattr(profile, 'education', '')}"
            )

            st.write(
                f"**Experience:** {getattr(profile, 'experience', '')}"
            )

            st.write(
                f"**Skills:** {getattr(profile, 'skills', '')}"
            )

            st.write(
                f"**Interests:** {getattr(profile, 'interests', '')}"
            )

            st.write(
                f"**Career Goal:** {getattr(profile, 'career_goal', '')}"
            )

        st.divider()

        if st.button(
            "🔍 Analyze My Career",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Analyzing your profile..."
            ):

                try:

                    assessment = analyze_career(
                        profile
                    )

                    st.session_state.assessment = assessment

                except Exception as e:

                    st.error(
                        f"Career analysis failed: {e}"
                    )

        # ----------------------------------------------------
        # SHOW ASSESSMENT
        # ----------------------------------------------------

        if st.session_state.assessment is not None:

            assessment = st.session_state.assessment

            st.success(
                "Career assessment completed!"
            )

            st.divider()

            st.subheader(
                "🎯 Recommended Career Paths"
            )

            # Handle common assessment structures
            recommendations = getattr(
                assessment,
                "recommended_careers",
                None,
            )

            if recommendations is None:
                recommendations = getattr(
                    assessment,
                    "career_paths",
                    None,
                )

            if recommendations:

                for i, career in enumerate(
                    recommendations,
                    start=1,
                ):

                    if isinstance(career, str):

                        st.markdown(
                            f"### {i}. {career}"
                        )

                    else:

                        title = getattr(
                            career,
                            "title",
                            None,
                        )

                        if title is None:
                            title = getattr(
                                career,
                                "name",
                                "Career Option",
                            )

                        st.markdown(
                            f"### {i}. {title}"
                        )

                        description = getattr(
                            career,
                            "description",
                            None,
                        )

                        if description:
                            st.write(description)

            else:

                st.write(assessment)

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

        st.write(
            "Based on your career assessment, focus on developing the skills below."
        )

        assessment = st.session_state.assessment

        # ----------------------------------------------------
        # TRY TO FIND SKILL DATA
        # ----------------------------------------------------

        skill_gaps = getattr(
            assessment,
            "skill_gaps",
            None,
        )

        if skill_gaps is None:

            skill_gaps = getattr(
                assessment,
                "missing_skills",
                None,
            )

        if skill_gaps:

            if isinstance(
                skill_gaps,
                dict,
            ):

                for skill, details in skill_gaps.items():

                    st.markdown(
                        f"### 🛠️ {skill}"
                    )

                    if isinstance(
                        details,
                        str,
                    ):
                        st.write(details)

                    else:
                        st.write(details)

            else:

                for skill in skill_gaps:

                    if isinstance(
                        skill,
                        str,
                    ):
                        st.markdown(
                            f"- {skill}"
                        )

                    else:

                        skill_name = getattr(
                            skill,
                            "name",
                            None,
                        )

                        if skill_name is None:
                            skill_name = str(skill)

                        st.markdown(
                            f"- {skill_name}"
                        )

        else:

            st.info(
                "No detailed skill-gap data was returned by the assessment."
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

        st.write(
            "Here is your personalized career development roadmap."
        )

        assessment = st.session_state.assessment

        roadmap = getattr(
            assessment,
            "roadmap",
            None,
        )

        if roadmap:

            # ------------------------------------------------
            # LIST ROADMAP
            # ------------------------------------------------

            if isinstance(
                roadmap,
                list,
            ):

                for i, step in enumerate(
                    roadmap,
                    start=1,
                ):

                    st.markdown(
                        f"### Step {i}"
                    )

                    if isinstance(
                        step,
                        str,
                    ):
                        st.write(step)

                    else:
                        st.write(step)

            elif isinstance(
                roadmap,
                dict,
            ):

                for title, details in roadmap.items():

                    st.markdown(
                        f"### {title}"
                    )

                    st.write(details)

            else:

                st.write(roadmap)

        else:

            # ------------------------------------------------
            # FALLBACK ROADMAP
            # ------------------------------------------------

            st.markdown(
                """
                ### 📚 Step 1 — Build Fundamentals

                Strengthen the core skills required for your target career.

                ### 🛠️ Step 2 — Practice

                Complete practical exercises and small projects.

                ### 💼 Step 3 — Build a Portfolio

                Create projects that demonstrate your abilities.

                ### 🎓 Step 4 — Advanced Learning

                Learn advanced concepts and tools relevant to your career.

                ### 🚀 Step 5 — Apply

                Start applying for internships, freelance work, or jobs.
                """
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

        st.caption(
            {
                "Beginner":
                    "Simple explanations with step-by-step guidance.",
                "Intermediate":
                    "More technical and practical guidance.",
                "Expert":
                    "Advanced career and technical guidance.",
            }[experience_level]
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
                st.write(user_prompt)

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
                    st.write(response)

            except Exception as e:

                st.error(
                    f"Could not get AI response: {e}"
                )
