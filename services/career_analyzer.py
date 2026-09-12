from models import CareerProfile, CareerAssessment

from services.gemini_client import generate_structured
from services.prompts import assessment_prompt
from services.esco_client import ESCOClient

from config import get_settings


def analyze_career(
    profile,
    gemini_api_key=None,
    model=None,
    esco_client=None,
) -> CareerAssessment:
    """
    Analyze a career profile.

    The function can be called simply as:

        analyze_career(profile)

    from app.py.

    API settings and ESCO client are created automatically.
    """

    settings = get_settings()

    # Use supplied values when available.
    if not gemini_api_key:
        gemini_api_key = settings.gemini_api_key

    if not model:
        model = settings.gemini_model

    # Create ESCO client automatically.
    if esco_client is None:
        esco_client = ESCOClient(
            settings.esco_base_url
        )

    # --------------------------------------------------------
    # Build ESCO search terms
    # --------------------------------------------------------

    search_terms = []

    degree = getattr(
        profile,
        "degree",
        "",
    )

    education = getattr(
        profile,
        "education",
        "",
    )

    career_goal = getattr(
        profile,
        "career_goal",
        "",
    )

    interests = getattr(
        profile,
        "interests",
        [],
    )

    if degree:
        search_terms.append(degree)

    if education and education not in search_terms:
        search_terms.append(education)

    if career_goal:
        search_terms.append(career_goal)

    if isinstance(interests, list):
        search_terms.extend(
            interests[:2]
        )

    elif isinstance(interests, str):
        search_terms.append(interests)

    # --------------------------------------------------------
    # Search ESCO
    # --------------------------------------------------------

    esco_lines = []
    seen = set()

    for term in search_terms:

        if not term:
            continue

        try:

            results = esco_client.search_occupations(
                term,
                limit=3,
            )

        except Exception:
            # ESCO is supporting information.
            # Career analysis should still work if ESCO
            # is temporarily unavailable.
            results = []

        for item in results:

            title = item.get(
                "title",
                "",
            ).strip()

            if not title:
                continue

            if title.lower() in seen:
                continue

            seen.add(
                title.lower()
            )

            description = item.get(
                "description",
                "",
            )

            esco_lines.append(
                f"- {title}: {description}"
            )

    context = "\n".join(
        esco_lines[:10]
    )

    # --------------------------------------------------------
    # Generate structured Gemini assessment
    # --------------------------------------------------------

    return generate_structured(
        assessment_prompt(
            profile,
            context,
        ),
        CareerAssessment,
        gemini_api_key,
        model,
    )
