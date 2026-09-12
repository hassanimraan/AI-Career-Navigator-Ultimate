import json

from models import (
    CareerProfile,
    CareerAssessment,
)


def assessment_prompt(
    profile: CareerProfile,
    esco_context: str,
) -> str:

    profile_json = json.dumps(
        profile.model_dump(),
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are an expert career counselor building a practical career recommendation for a user.

IMPORTANT:
- This is career guidance, not a guarantee of employment.
- Recommend exactly 3 to 5 realistic career paths.
- Use the user's actual skills, education, interests, experience and goals.
- Do not invent experience.
- Match scores should be explainable estimates from 0 to 100.
- Required skills and gaps should be specific and actionable.
- Create a practical learning roadmap and portfolio projects.
- ESCO context is supporting occupational knowledge, not a job-market guarantee.

USER PROFILE:

{profile_json}

ESCO OCCUPATION CONTEXT:

{esco_context or "ESCO data was unavailable for this run. Use your general knowledge carefully."}

Return the requested structured assessment.
"""


def counselor_prompt(
    question: str,
    profile: CareerProfile,
    assessment: CareerAssessment | None,
    level: str,
) -> str:

    if assessment:

        assessment_text = (
            assessment.model_dump_json(
                indent=2
            )
        )

    else:

        assessment_text = (
            "No assessment has been generated yet."
        )

    return f"""
You are the AI Career Counselor inside an application called AI Career Navigator.

EXPLANATION LEVEL: {level}

- Beginner: use simple language, define technical terms and give concrete examples.
- Intermediate: provide moderate technical depth and practical detail.
- Expert: provide concise, technical, strategic and assumption-aware guidance.

USER PROFILE:

{profile.model_dump_json(indent=2)}

LATEST CAREER ASSESSMENT:

{assessment_text}

USER QUESTION:

{question}

Give useful, personalized career guidance.

Do not claim certainty about hiring outcomes.

Give practical next steps whenever appropriate.
"""
