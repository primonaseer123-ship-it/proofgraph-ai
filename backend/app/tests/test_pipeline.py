import pytest
import time
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.init_db import init_db_schema

SAMPLE_JAVA_PROJECT_REPORT = """
Library Management System (FAST-NUCES Semester 3 Project)
Author: Hamza CS-2023

Architecture & Implementation:
The system is constructed using core Java and Object-Oriented Programming principles.
We implemented inheritance and polymorphism:
public class LibraryItem {
    protected String itemId;
    protected String title;
}
public class Book extends LibraryItem {
    private String isbn;
}
public interface Authenticable {
    public boolean authenticate(String username, String password);
}

Database Integration:
Relational persistence is handled through JDBC and MySQL:
Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/library_db", "user", "pass");
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM books WHERE isbn = ?");
CREATE TABLE books (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    isbn VARCHAR(50) UNIQUE
);
CRUD operations, user authentication, and transaction handling were successfully implemented.
"""

@pytest.mark.asyncio
async def test_full_proofgraph_pipeline():
    # 1. Initialize schema
    await init_db_schema()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check health
        health_resp = await client.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["anti_hallucination_rule"] == "NO EVIDENCE -> NO FACTUAL CLAIM"

        # 2. Register demo student (Hamza from FAST-NUCES)
        unique_email = f"hamza_{int(time.time())}@example.edu.pk"
        register_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Hamza Tariq",
            "institution": "FAST-NUCES Lahore",
            "degree_program": "BS Computer Science",
            "role": "student"
        }
        reg_resp = await client.post("/api/v1/auth/register", json=register_payload)
        assert reg_resp.status_code == 200

        # Login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "Password123!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. User asserts 2 claims:
        # Claim A: Advanced Java (Supported by project)
        # Claim B: Expert Machine Learning (Unsupported ghost claim)
        claim_a_resp = await client.post("/api/v1/claims", json={
            "skill_slug": "java",
            "stated_proficiency": "Advanced",
            "claim_text": "Advanced Java Developer with deep expertise in enterprise OOP and databases"
        }, headers=headers)
        assert claim_a_resp.status_code == 200

        claim_b_resp = await client.post("/api/v1/claims", json={
            "skill_slug": "machine-learning",
            "stated_proficiency": "Expert",
            "claim_text": "Production Machine Learning Engineer training deep neural networks"
        }, headers=headers)
        assert claim_b_resp.status_code == 200

        # 4. Upload Evidence: The Java Library Management System report
        ev_resp = await client.post("/api/v1/evidence/manual", json={
            "title": "FAST-NUCES Library Management System Report",
            "source_type": "project_report",
            "raw_text": SAMPLE_JAVA_PROJECT_REPORT,
            "evidence_date": "2025-11-15",
            "technologies": ["Java", "OOP", "JDBC", "SQL", "MySQL"]
        }, headers=headers)
        assert ev_resp.status_code == 200

        # 5. Execute Multi-Agent Pipeline
        pipeline_resp = await client.post("/api/v1/agents/run", headers=headers)
        assert pipeline_resp.status_code == 200
        pipeline_data = pipeline_resp.json()
        assert pipeline_data["success"] is True

        # Verify Agent outputs:
        # A. Evidence Extractor isolated Java OOP, JDBC, and SQL
        ev_items = pipeline_data["extracted_evidence"]["evidence_items"]
        extracted_techs = [t for item in ev_items for t in item["extracted_technologies"]]
        assert "Java OOP" in extracted_techs
        assert "JDBC" in extracted_techs
        assert "SQL" in extracted_techs

        # B. Contradiction Detector flagged Machine Learning as a GHOST CLAIM or EXAGGERATION
        contradictions = pipeline_data["contradiction_report"]["contradictions_found"]
        ml_flags = [c for c in contradictions if "machine-learning" in c["claim_text"].lower()]
        assert len(ml_flags) > 0, "Contradiction Agent must flag unsupported Machine Learning claim!"

        # 6. Query the Evidence Graph
        graph_resp = await client.get("/api/v1/graph", headers=headers)
        assert graph_resp.status_code == 200
        graph_data = graph_resp.json()
        assert len(graph_data["nodes"]) > 0
        assert len(graph_data["edges"]) > 0

        # 7. Generate Application Package (Zero-Hallucination Resume)
        app_resp = await client.post("/api/v1/applications/generate", json={
            "target_role": "Junior Backend Engineer",
            "target_company": "Systems Limited",
            "document_type": "resume"
        }, headers=headers)
        assert app_resp.status_code == 200
        app_data = app_resp.json()
        
        # Verify Zero-Hallucination rule:
        # The unsupported Machine Learning claim MUST be omitted!
        assert any("machine-learning" in omitted.lower() for omitted in app_data["unsupported_claims_omitted"])
        assert "Production Machine Learning" not in app_data["markdown_content"]
        # The Java claim MUST be cited!
        assert "JAVA" in app_data["markdown_content"]
        assert len(app_data["grounded_citations"]) > 0

        print("\nAll pipeline assertions PASSED: ProofGraph successfully caught contradiction and verified grounded skills!")
