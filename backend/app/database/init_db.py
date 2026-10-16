import asyncio
from app.database.session import engine
from app.database.base import Base
from app.database.session import AsyncSessionLocal
from app.models.skill import Skill, SkillRelationship
from app.models.opportunity import Opportunity, OpportunityRequirement
from sqlalchemy import select

STANDARD_SKILLS = [
    # Top-Level Categories
    {"slug": "software-development", "name": "Software Development", "category": "General", "taxonomy_path": "Software Development", "level_depth": 1},
    {"slug": "programming-languages", "name": "Programming Languages", "category": "Languages", "taxonomy_path": "Software Development/Languages", "level_depth": 2},
    
    # Java Tree
    {"slug": "java", "name": "Java", "category": "Languages", "taxonomy_path": "Software Development/Languages/Java", "level_depth": 3},
    {"slug": "java-oop", "name": "Object-Oriented Programming (Java)", "category": "Languages", "taxonomy_path": "Software Development/Languages/Java/OOP", "level_depth": 4},
    {"slug": "java-jdbc", "name": "JDBC & Database Integration", "category": "Languages", "taxonomy_path": "Software Development/Languages/Java/JDBC", "level_depth": 4},
    {"slug": "java-spring", "name": "Spring Boot", "category": "Frameworks", "taxonomy_path": "Software Development/Languages/Java/Spring", "level_depth": 4},
    {"slug": "oop-inheritance", "name": "Inheritance & Polymorphism", "category": "Foundations", "taxonomy_path": "Software Development/Foundations/OOP/Inheritance", "level_depth": 5},
    {"slug": "oop-interfaces", "name": "Interfaces & Abstraction", "category": "Foundations", "taxonomy_path": "Software Development/Foundations/OOP/Interfaces", "level_depth": 5},
    
    # Python Tree
    {"slug": "python", "name": "Python", "category": "Languages", "taxonomy_path": "Software Development/Languages/Python", "level_depth": 3},
    {"slug": "python-scripting", "name": "Python Scripting & Automation", "category": "Languages", "taxonomy_path": "Software Development/Languages/Python/Scripting", "level_depth": 4},
    {"slug": "machine-learning", "name": "Machine Learning", "category": "Data Science", "taxonomy_path": "Data Science/Machine Learning", "level_depth": 3},
    {"slug": "deep-learning", "name": "Deep Learning & Neural Networks", "category": "Data Science", "taxonomy_path": "Data Science/Deep Learning", "level_depth": 4},
    
    # C++
    {"slug": "cpp", "name": "C++", "category": "Languages", "taxonomy_path": "Software Development/Languages/C++", "level_depth": 3},
    {"slug": "data-structures", "name": "Data Structures & Algorithms", "category": "Foundations", "taxonomy_path": "Software Development/Foundations/DSA", "level_depth": 3},
    
    # Databases
    {"slug": "sql", "name": "SQL & Relational Databases", "category": "Databases", "taxonomy_path": "Databases/Relational/SQL", "level_depth": 3},
    {"slug": "mysql", "name": "MySQL", "category": "Databases", "taxonomy_path": "Databases/Relational/MySQL", "level_depth": 4},
    {"slug": "postgresql", "name": "PostgreSQL", "category": "Databases", "taxonomy_path": "Databases/Relational/PostgreSQL", "level_depth": 4},
    
    # Web Development
    {"slug": "web-frontend", "name": "Frontend Web Development", "category": "Web", "taxonomy_path": "Web Development/Frontend", "level_depth": 2},
    {"slug": "html-css", "name": "HTML5 & CSS3", "category": "Web", "taxonomy_path": "Web Development/Frontend/HTML-CSS", "level_depth": 3},
    {"slug": "javascript", "name": "JavaScript (ES6+)", "category": "Languages", "taxonomy_path": "Software Development/Languages/JavaScript", "level_depth": 3},
    {"slug": "react", "name": "React.js", "category": "Web", "taxonomy_path": "Web Development/Frontend/React", "level_depth": 4},
    {"slug": "fastapi", "name": "FastAPI", "category": "Backend", "taxonomy_path": "Web Development/Backend/FastAPI", "level_depth": 4},
    
    # Tools & Soft Skills
    {"slug": "git", "name": "Git & Version Control", "category": "DevOps", "taxonomy_path": "DevOps/Version Control/Git", "level_depth": 3},
    {"slug": "leadership", "name": "Leadership & Project Management", "category": "Soft Skills", "taxonomy_path": "Soft Skills/Leadership", "level_depth": 2},
]

STANDARD_RELATIONSHIPS = [
    ("programming-languages", "java", "parent_child"),
    ("java", "java-oop", "parent_child"),
    ("java", "java-jdbc", "parent_child"),
    ("java", "java-spring", "parent_child"),
    ("java-oop", "oop-inheritance", "parent_child"),
    ("java-oop", "oop-interfaces", "parent_child"),
    ("programming-languages", "python", "parent_child"),
    ("python", "python-scripting", "parent_child"),
    ("python", "machine-learning", "related"),
    ("machine-learning", "deep-learning", "parent_child"),
    ("programming-languages", "cpp", "parent_child"),
    ("cpp", "data-structures", "related"),
    ("sql", "mysql", "parent_child"),
    ("sql", "postgresql", "parent_child"),
    ("web-frontend", "html-css", "parent_child"),
    ("web-frontend", "javascript", "parent_child"),
    ("javascript", "react", "parent_child"),
]

DEMO_OPPORTUNITIES = [
    {
        "title": "Junior Java Backend Engineering Intern",
        "organization": "Systems Limited (Lahore, PK)",
        "opportunity_type": "internship",
        "location": "Lahore / Hybrid",
        "external_url": "https://systemsltd.com/careers",
        "description": "Looking for passionate 3rd/4th year CS students with demonstrated competence in core Java, Object-Oriented Design, and relational databases.",
        "requirements": [
            ("java", "Intermediate", True),
            ("java-oop", "Intermediate", True),
            ("sql", "Intermediate", True),
            ("git", "Beginner", True),
            ("java-spring", "Beginner", False)
        ]
    },
    {
        "title": "Full-Stack Web Development Fellow",
        "organization": "Arbisoft (Lahore, PK)",
        "opportunity_type": "internship",
        "location": "Lahore / Remote",
        "external_url": "https://arbisoft.com/careers",
        "description": "Join our fast-paced engineering team building scalable web applications with React, modern JavaScript, and clean APIs.",
        "requirements": [
            ("javascript", "Intermediate", True),
            ("react", "Intermediate", True),
            ("html-css", "Intermediate", True),
            ("git", "Intermediate", True),
            ("fastapi", "Beginner", False)
        ]
    },
    {
        "title": "Undergraduate Research Assistant in Applied AI",
        "organization": "National Center of Artificial Intelligence (NCAI, PK)",
        "opportunity_type": "scholarship",
        "location": "Islamabad / Hybrid",
        "external_url": "https://ncai.pide.org.pk",
        "description": "Research grant fellowship for students with verifiable machine learning projects, mathematical grounding, and Python codebase experience.",
        "requirements": [
            ("python", "Advanced", True),
            ("machine-learning", "Intermediate", True),
            ("data-structures", "Intermediate", True),
            ("deep-learning", "Beginner", False)
        ]
    }
]

async def init_db_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Seed skills if not present
        existing_skills = await session.execute(select(Skill))
        if not existing_skills.scalars().first():
            for item in STANDARD_SKILLS:
                skill = Skill(**item)
                session.add(skill)
            await session.commit()
            
            for parent, child, rel_type in STANDARD_RELATIONSHIPS:
                rel = SkillRelationship(parent_slug=parent, child_slug=child, relation_type=rel_type)
                session.add(rel)
            await session.commit()
            
        # Seed opportunities if not present
        existing_opps = await session.execute(select(Opportunity))
        if not existing_opps.scalars().first():
            for opp_data in DEMO_OPPORTUNITIES:
                reqs = opp_data.pop("requirements")
                opp = Opportunity(**opp_data)
                session.add(opp)
                await session.flush()
                for skill_slug, min_prof, is_mand in reqs:
                    req = OpportunityRequirement(
                        opportunity_id=opp.id,
                        skill_slug=skill_slug,
                        minimum_proficiency=min_prof,
                        is_mandatory=is_mand
                    )
                    session.add(req)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db_schema())
    print("Database tables initialized and standard ontology seeded successfully.")
