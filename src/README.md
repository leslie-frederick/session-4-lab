# Slalom Capabilities Management API

<p align="center">
  <img src="./.images/byte-teacher.png" alt="Byte Teacher" width="200" />
</p>

A FastAPI application that enables Slalom consultants to register their capabilities and manage consulting expertise across the organization.

## Features

- View all available consulting capabilities
- Register consultant expertise and availability
- Track skill levels and certifications
- Manage capability capacity and team assignments

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc
   - Capabilities Dashboard: http://localhost:8000/

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/capabilities`                                                   | Get all capabilities with details and current consultant assignments |
| POST   | `/capabilities/{capability_name}/register?email=consultant@slalom.com` | Register consultant for a capability                     |
| DELETE | `/capabilities/{capability_name}/unregister?email=consultant@slalom.com` | Unregister consultant from a capability              |

## Data Model

The application uses a consulting-focused data model:

1. **Capabilities** - Uses capability name as identifier:
   - Description of the consulting capability
   - Skill levels (Emerging, Proficient, Advanced, Expert)
   - Practice area (Strategy, Technology, Operations)
   - Industry verticals served
   - Required certifications
   - List of consultant emails registered
   - Available capacity (hours per week)
   - Geographic location preferences

2. **Consultants** - Uses email as identifier:
   - Name
   - Practice area
   - Skill level
   - Certifications
   - Availability

## Persistent Storage

The API now uses a SQLite database for persistent capability and registration data.

- Default database path: `src/data/capabilities.db`
- Data is seeded automatically on first run
- Existing endpoint response shape remains the same

### Configuration

Use `CAPABILITIES_DB_PATH` to configure where the database file is stored.

Examples:

Local development:

```
CAPABILITIES_DB_PATH=./src/data/capabilities.db uvicorn app:app --reload
```

Cloud/container environment:

```
CAPABILITIES_DB_PATH=/var/lib/slalom/capabilities.db uvicorn app:app --host 0.0.0.0 --port 8000
```

## Future Enhancements

This exercise will guide you through implementing:
- Capability maturity assessments
- Intelligent team matching algorithms  
- Analytics dashboards for practice leads
- Integration with project management systems
- Advanced search and filtering capabilities
