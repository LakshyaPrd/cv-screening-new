"""
Predefined dictionaries for skills, tools, and role matching.
In production, these would be stored in the database and manageable via admin panel.
"""


def get_skills_dict():
    """
    Get list of recognized skills.
    This is a starter list - should be expanded based on domain.
    """
    return [
        # Programming
        "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust",
        
        # Web Development
        "html", "css", "react", "vue", "angular", "node.js", "django", "flask", "fastapi",
        "next.js", "express", "spring", "asp.net",
        
        # BIM & Architecture (based on SOW example)
        "bim", "revit", "autocad", "navisworks", "3ds max", "sketchup", "rhinoceros",
        "archicad", "civil 3d", "infraworks", "lumion", "enscape",
        
        # Project Management
        "project management", "agile", "scrum", "kanban", "jira", "asana", "trello",
        
        # Data & Analytics
        "sql",  "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "data analysis", "machine learning", "deep learning", "tensorflow", "pytorch",
        
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "gitlab ci",
        
        # Design
        "photoshop", "illustrator", "figma", "sketch", "adobe xd", "indesign",
        
        # General
        "microsoft office", "excel", "powerpoint", "word", "google workspace",
        "communication", "leadership", "teamwork", "problem solving",
    ]


def get_tools_dict():
    """
    Get list of recognized software/tools.
    Focused on BIM/Architecture as per SOW, but expandable.
    """
    return [
        # BIM & CAD
        "revit",
        "autocad",
        "navisworks",
        "bim 360",
        "autodesk construction cloud",
        "civil 3d",
        "sketchup",
        "archicad",
        "rhinoceros",
        "grasshopper",
        "dynamo",
        
        # Rendering & Visualization
        "lumion",
        "enscape",
        "v-ray",
        "3ds max",
        "blender",
        
        # Project Management
        "procore",
        "plangrid",
        "primavera",
        "ms project",
        
        # General
        "microsoft office",
        "adobe creative suite",
        "photoshop",
        "illustrator",
        "indesign",
    ]


def get_role_equivalents():
    """
    Get dictionary of role title equivalents for matching.
    """
    return {
        "bim architect": ["bim designer", "architectural designer", "design architect"],
        "bim manager": ["bim coordinator", "bim lead", "vdc manager"],
        "project manager": ["pm", "program manager", "project lead"],
        "software engineer": ["developer", "programmer", "software developer"],
        "senior developer": ["lead developer", "principal engineer", "staff engineer"],
        "data scientist": ["ml engineer", "data analyst", "research scientist"],
        "ui/ux designer": ["product designer", "ux designer", "interaction designer"],
    }
