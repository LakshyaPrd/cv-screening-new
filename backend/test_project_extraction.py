"""
Test script to demonstrate the new project extraction feature.
Shows how projects are now extracted as separate structured data.
"""

from app.services.ats_parser import ATSParser

# Sample CV text with project information
sample_cv_text = """
John Doe
BIM Engineer
john.doe@example.com | +971 50 123 4567
Dubai, UAE

SUMMARY
Experienced BIM Engineer with 8+ years in Civil Engineering and BIM Modeling.
Specialized in high-rise buildings and infrastructure projects across GCC region.

WORK EXPERIENCE

BIM Engineer | XYZ Consultancy
Jan 2020 - Present
Leading BIM coordination for mega projects in Saudi Arabia and UAE.
Responsible for clash detection and resolution using Navisworks.

Senior Modeler | ABC Engineering LLC
Jun 2017 - Dec 2019
Created detailed structural models for commercial and residential projects.
Collaborated with architects and MEP teams for integrated design.

PROJECTS

1. Riyadh Metro Station - Phase 2
Site: Riyadh, Saudi Arabia
Role: BIM Coordinator
Duration: Jan 2022 - Dec 2023
- Coordinated BIM models across 5 disciplines
- Managed clash detection and resolution
- Delivered As-Built documentation for 3 stations
- Reduced design conflicts by 40% through proactive coordination

2. Dubai Marina Residential Tower (G+45)
Location: Dubai Marina, UAE
Position: Lead BIM Modeler
Jan 2021 - Dec 2021
- Developed detailed architectural and structural models in Revit
- Created construction drawings and shop drawings
- Coordinated with MEP consultants for services integration
- Managed model quality and LOD requirements

3. Abu Dhabi Airport Expansion Project
Site: Abu Dhabi, UAE
Role: Structural BIM Engineer
Duration: Jun 2019 - Dec 2020
Responsible for structural steel modeling and detailing
Performed quantity take-offs and bill of materials generation
Coordinated with construction team for buildability reviews

4. King Abdullah Financial District - Commercial Complex
Riyadh, KSA
Senior Modeler
Apr 2018 - May 2019
- Modeled 3 commercial buildings (B+2+G+20 each)
- Developed families and templates for project standardization
- Conducted BIM training for junior engineers

EDUCATION
Bachelor of Engineering in Civil Engineering
University of Technology, 2015

SKILLS
Structural Design, BIM Coordination, Clash Detection, Quantity Surveying

TOOLS
Revit, Navisworks, AutoCAD, Tekla Structures
"""


def test_project_extraction():
    print("=" * 80)
    print("TESTING NEW PROJECT EXTRACTION FEATURE")
    print("=" * 80)

    parser = ATSParser()
    result = parser.parse(sample_cv_text)

    print("\n📋 BASIC INFO:")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Position: {result['position']}")
    print(f"Discipline: {result['discipline']}")

    print("\n💼 WORK EXPERIENCE (Separate from Projects):")
    print(f"Total Experience Entries: {len(result['experience'])}")
    for i, exp in enumerate(result['experience'], 1):
        print(f"\n  Experience #{i}:")
        print(f"  - Job Title: {exp['job_title']}")
        print(f"  - Company: {exp['company']}")
        print(f"  - Duration: {exp['start_date']} to {exp['end_date']}")
        print(f"  - Description Lines: {len(exp['description'])}")

    print("\n" + "=" * 80)
    print("🏗️ PROJECTS (NEW STRUCTURED FORMAT):")
    print("=" * 80)
    print(f"Total Projects Found: {len(result['projects'])}")

    for i, project in enumerate(result['projects'], 1):
        print(f"\n{'─' * 80}")
        print(f"PROJECT #{i}")
        print(f"{'─' * 80}")
        print(f"📌 Project Name: {project['project_name']}")
        print(f"📍 Site/Location: {project['site_name']}")
        print(f"👤 Role: {project['role']}")
        print(f"📅 Duration: {project['duration_start']} to {project['duration_end']}")
        print(f"\n📝 Responsibilities ({len(project['responsibilities'])} items):")
        for j, resp in enumerate(project['responsibilities'], 1):
            print(f"   {j}. {resp}")

    print("\n" + "=" * 80)
    print("✅ SKILLS & TOOLS:")
    print("=" * 80)
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"Tools: {', '.join(result['tools'])}")

    print("\n" + "=" * 80)
    print("📚 EDUCATION:")
    print("=" * 80)
    for edu in result['education']:
        print(f"- {edu['degree']} ({edu['year']})")

    print("\n" + "=" * 80)
    print("✨ SUMMARY")
    print("=" * 80)
    print(result['summary'])

    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    test_project_extraction()
