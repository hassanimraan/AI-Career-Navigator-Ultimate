from models import CareerProfile
from config import get_settings

profile = CareerProfile.from_form(
    education="Bachelor's",
    degree="Computer Science",
    skill_text="Python: intermediate\nSQL: beginner",
    interests="AI, data analysis",
    work_preferences=["Remote"],
    experience="University project",
    career_goal="Become a data analyst",
)

assert profile.skills[0].name == "Python"
assert profile.skills[0].level == 60
assert profile.skills[1].level == 30

settings = get_settings()
print("Import/model test: OK")
print("Default Gemini model:", settings.gemini_model)
print("Profile parsing test: OK")
print("Project files are ready.")
