"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

import json
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Slalom Capabilities Management API",
              description="API for managing consulting capabilities and consultant expertise")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Default seed data for first-time database initialization.
CAPABILITIES_SEED = {
    "Cloud Architecture": {
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,  # hours per week available across team
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
    },
    "Data Analytics": {
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology", 
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
    },
    "DevOps Engineering": {
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"], 
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
    },
    "Digital Strategy": {
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
    },
    "Change Management": {
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
    },
    "UX/UI Design": {
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
    },
    "Cybersecurity": {
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
    },
    "Business Intelligence": {
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
    },
    "Agile Coaching": {
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
    }
}


def get_database_path() -> Path:
    """Resolve database path from environment with a local default."""
    configured_path = os.getenv("CAPABILITIES_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return current_dir / "data" / "capabilities.db"


class CapabilityRepository:
    """SQLite-backed repository for capabilities and registrations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self, seed_data: dict):
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS capabilities (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    practice_area TEXT NOT NULL,
                    skill_levels_json TEXT NOT NULL,
                    certifications_json TEXT NOT NULL,
                    industry_verticals_json TEXT NOT NULL,
                    capacity INTEGER NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS capability_registrations (
                    capability_name TEXT NOT NULL,
                    consultant_email TEXT NOT NULL,
                    PRIMARY KEY (capability_name, consultant_email),
                    FOREIGN KEY (capability_name) REFERENCES capabilities(name) ON DELETE CASCADE
                )
                """
            )

            cursor.execute("SELECT COUNT(*) AS count FROM capabilities")
            if cursor.fetchone()["count"] > 0:
                return

            for capability_name, details in seed_data.items():
                cursor.execute(
                    """
                    INSERT INTO capabilities (
                        name,
                        description,
                        practice_area,
                        skill_levels_json,
                        certifications_json,
                        industry_verticals_json,
                        capacity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        capability_name,
                        details["description"],
                        details["practice_area"],
                        json.dumps(details["skill_levels"]),
                        json.dumps(details["certifications"]),
                        json.dumps(details["industry_verticals"]),
                        details["capacity"],
                    ),
                )

                for email in details["consultants"]:
                    cursor.execute(
                        """
                        INSERT INTO capability_registrations (capability_name, consultant_email)
                        VALUES (?, ?)
                        """,
                        (capability_name, email),
                    )

            connection.commit()

    def get_capabilities(self):
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    name,
                    description,
                    practice_area,
                    skill_levels_json,
                    certifications_json,
                    industry_verticals_json,
                    capacity
                FROM capabilities
                ORDER BY name
                """
            )
            capability_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT capability_name, consultant_email
                FROM capability_registrations
                ORDER BY capability_name, consultant_email
                """
            )
            registration_rows = cursor.fetchall()

        consultant_map = {}
        for row in registration_rows:
            capability_name = row["capability_name"]
            consultant_map.setdefault(capability_name, []).append(row["consultant_email"])

        capabilities = {}
        for row in capability_rows:
            capability_name = row["name"]
            capabilities[capability_name] = {
                "description": row["description"],
                "practice_area": row["practice_area"],
                "skill_levels": json.loads(row["skill_levels_json"]),
                "certifications": json.loads(row["certifications_json"]),
                "industry_verticals": json.loads(row["industry_verticals_json"]),
                "capacity": row["capacity"],
                "consultants": consultant_map.get(capability_name, []),
            }

        return capabilities

    def register_for_capability(self, capability_name: str, email: str):
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM capabilities WHERE name = ?", (capability_name,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Capability not found")

            cursor.execute(
                """
                SELECT 1
                FROM capability_registrations
                WHERE capability_name = ? AND consultant_email = ?
                """,
                (capability_name, email),
            )
            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=400,
                    detail="Consultant is already registered for this capability",
                )

            cursor.execute(
                """
                INSERT INTO capability_registrations (capability_name, consultant_email)
                VALUES (?, ?)
                """,
                (capability_name, email),
            )
            connection.commit()

    def unregister_from_capability(self, capability_name: str, email: str):
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM capabilities WHERE name = ?", (capability_name,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Capability not found")

            cursor.execute(
                """
                DELETE FROM capability_registrations
                WHERE capability_name = ? AND consultant_email = ?
                """,
                (capability_name, email),
            )
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Consultant is not registered for this capability",
                )

            connection.commit()


repository = CapabilityRepository(get_database_path())
repository.initialize(CAPABILITIES_SEED)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities():
    return repository.get_capabilities()


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str):
    """Register a consultant for a capability"""
    repository.register_for_capability(capability_name, email)
    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str):
    """Unregister a consultant from a capability"""
    repository.unregister_from_capability(capability_name, email)
    return {"message": f"Unregistered {email} from {capability_name}"}
