"""
Test script for real CV data from Devarsh K Prakash
"""

from app.services.ats_parser import ATSParser

# Sample CV text from your actual CV
real_cv_text = """
DEVARSH K PRAKASH
BIM Engineer

Email: devarshprakash1210@gmail.com
Phone: +917909125884

SUMMARY
BIM Engineer with over 2 years of experience delivering architectural and structural models for US, GCC, and European markets. Skilled in Revit, Navisworks, and Scan-to-BIM processes, with a strong foundation in clash detection, coordination, and technical documentation.

WORK EXPERIENCE

Duncan and Ross Technology and Engineering Solution
December 2024 — Present
- Developed and coordinated 3D BIM models for complex architectural and structural projects
- Managed data in BIM 360, ensuring seamless communication among stakeholders
- Produced high-quality project documentation

Delta T MEP — Bangalore, India
March 2024 — October 2024
- Created 3D models for architectural and structural systems for US clients using Revit
- Performed clash detection using Navisworks and developed project deliverables including GA drawings
- Utilized Scan-to-BIM workflows to generate accurate models from point cloud data

April 2023 — March 2024
- Produced architectural and structural models for GCC projects using BIM tools
- Generated 2D drawings and 3D models of building components

PROJECTS

AMANSAMAR HOTEL & RESIDENCES — Hospitality Resort, Wadi Safar, Riyadh (GCC)
Role: BIM Modeler
Duration: 2023-2024
- Developed architectural BIM models in Revit for a high-end hospitality project
- Created IFC (Issued for Construction) drawings and coordinated with the design team
- Delivered LOD 300 models and comprehensive construction documentation

AL MARYAH — Commercial Building, Al Maryah Island (Abu Dhabi, UAE)
Role: Structural BIM Engineer
Duration: 2023
- Developed high-detail structural BIM models in Revit at LOD 400-500, ensuring design accuracy
- Integrated model data and parameters to support coordination, shop drawing development
- Created structural shop drawings directly from the coordinated Revit model
- Ensured consistency with MEP and architectural disciplines for final deliverables

BELMONT WEST WOOD VILLAGE — G+6 Commercial Building, California, USA
Role: BIM Modeler
Duration: 2023
- Modeled both architectural and structural elements using Revit based on US standards
- Performed clash detection in Navisworks and produced general arrangement (GA) drawings
- Coordinated with the client to resolve design conflicts and submitted detailed LOD 300 sheets

EDUCATION
Bachelor of Engineering (B.E.), Civil Engineering
CMS College of Engineering and Technology — Coimbatore, India
Graduated 2023 | CGPA: 8.51/10

SKILLS
Revit, AutoCAD, Navisworks, Dynamo, BIM 360, Communication, Documentation

CERTIFICATIONS
Autodesk Revit For BIM, 2023
Autodesk AutoCAD Design & Drafting, 2023
"""


def test_real_cv():
    print("=" * 80)
    print("TESTING WITH REAL CV - DEVARSH K PRAKASH")
    print("=" * 80)

    parser = ATSParser()
    result = parser.parse(real_cv_text)

    print("\n📋 BASIC INFO:")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Position: {result['position']}")
    print(f"Discipline: {result['discipline']}")

    print("\n" + "=" * 80)
    print("🏗️ PROJECTS EXTRACTED:")
    print("=" * 80)
    print(f"Total Projects Found: {len(result['projects'])}")

    if len(result['projects']) == 0:
        print("\n⚠️ WARNING: No projects were extracted!")
        print("This might indicate an issue with the project detection logic.")

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
    print("💼 WORK EXPERIENCE:")
    print("=" * 80)
    print(f"Total Experience Entries: {len(result['experience'])}")

    for i, exp in enumerate(result['experience'], 1):
        print(f"\n  Experience #{i}:")
        print(f"  - Job Title: {exp['job_title']}")
        print(f"  - Company: {exp['company']}")
        print(f"  - Duration: {exp['start_date']} to {exp['end_date']}")
        print(f"  - Description Lines: {len(exp['description'])}")

    print("\n" + "=" * 80)
    print("✅ SKILLS & TOOLS:")
    print("=" * 80)
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"Tools: {', '.join(result['tools'])}")

    print("\n" + "=" * 80)
    print("EXPECTED PROJECTS:")
    print("=" * 80)
    print("Should extract 3 projects:")
    print("1. AMANSAMAR HOTEL & RESIDENCES (Riyadh)")
    print("2. AL MARYAH (Abu Dhabi)")
    print("3. BELMONT WEST WOOD VILLAGE (California)")


if __name__ == "__main__":
    test_real_cv()
