from models import CareerProfile, CareerAssessment
from services.gemini_client import generate_structured
from services.prompts import assessment_prompt

def analyze_career(profile, gemini_api_key, model, esco_client) -> CareerAssessment:
    # Search ESCO using the user's degree, interests and goal to provide grounding context.
    search_terms = [profile.degree, profile.career_goal] + profile.interests[:2]
    esco_lines = []
    seen = set()

    for term in search_terms:
        for item in esco_client.search_occupations(term, limit=3):
            title = item.get("title", "").strip()
            if title and title.lower() not in seen:
                seen.add(title.lower())
                desc = item.get("description", "")
                esco_lines.append(f"- {title}: {desc}")

    context = "\n".join(esco_lines[:10])
    return generate_structured(
        assessment_prompt(profile, context),
        CareerAssessment,
        gemini_api_key,
        model,
    )
