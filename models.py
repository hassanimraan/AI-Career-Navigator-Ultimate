from typing import List
from pydantic import BaseModel, Field


# ============================================================
# SKILL
# ============================================================

class Skill(BaseModel):
    name: str
    level: int = Field(ge=0, le=100)


# ============================================================
# CAREER PROFILE
# ============================================================

class CareerProfile(BaseModel):
    education: str
    degree: str
    skills: List[Skill]
    interests: List[str]
    work_preferences: List[str]
    experience: str
    career_goal: str
    cv_text: str = ""

    @classmethod
    def from_form(
        cls,
        education: str,
        degree: str,
        skill_text: str,
        interests: str,
        work_preferences: List[str],
        experience: str,
        career_goal: str,
        cv_text: str = "",
    ):
        skills = []

        for line in skill_text.splitlines():
            line = line.strip()

            if not line:
                continue

            if ":" in line:
                name, raw = line.split(":", 1)
                name = name.strip()
                raw = raw.strip().lower()

                level_map = {
                    "beginner": 30,
                    "basic": 30,
                    "intermediate": 60,
                    "advanced": 85,
                    "expert": 100,
                }

                try:
                    level = int(raw)
                except ValueError:
                    level = level_map.get(raw, 50)

            else:
                name = line
                level = 50

            if name:
                skills.append(
                    Skill(
                        name=name,
                        level=max(0, min(100, level)),
                    )
                )

        return cls(
            education=education.strip(),
            degree=degree.strip(),
            skills=skills,
            interests=[
                x.strip()
                for x in interests.split(",")
                if x.strip()
            ],
            work_preferences=work_preferences,
            experience=experience.strip(),
            career_goal=career_goal.strip(),
            cv_text=cv_text[:20000],
        )


# ============================================================
# SKILL GAP
# ============================================================

class SkillGap(BaseModel):
    skill: str
    current_level: int = Field(ge=0, le=100)
    required_level: int = Field(ge=0, le=100)
    gap_score: int = Field(ge=0, le=100)


# ============================================================
# ROADMAP
# ============================================================

class RoadmapItem(BaseModel):
    phase: str
    timeframe: str
    objective: str
    topics: List[str]
    deliverable: str


# ============================================================
# PROJECT RECOMMENDATION
# ============================================================

class ProjectRecommendation(BaseModel):
    title: str
    description: str
    skills: List[str]


# ============================================================
# CAREER MATCH
# ============================================================

class CareerMatch(BaseModel):
    career_title: str

    match_score: int = Field(
        ge=0,
        le=100,
    )

    reason: str

    esco_context: str = ""

    required_skills: List[str]

    missing_skills: List[str]

    skill_gaps: List[SkillGap]

    learning_roadmap: List[RoadmapItem]

    recommended_projects: List[ProjectRecommendation]

    next_steps: List[str]


# ============================================================
# CAREER ASSESSMENT
# ============================================================

class CareerAssessment(BaseModel):
    summary: str

    strengths: List[str]

    matches: List[CareerMatch]
