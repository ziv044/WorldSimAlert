# 01 - Project Setup & Tech Stack

## Overview

A single-player country simulation game combining city-builder economics (SimCity), grand strategy depth (Victoria), and military realism (Red Alert). Players manage real countries with real-ish data, making decisions that ripple through interconnected systems.

---

## Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Backend | Python 3.11+ (FastAPI) | Fast async API, type hints, easy testing |
| Frontend | Vanilla HTML/CSS/JS | Simple, no build step, rapid iteration |
| Database | JSON files in `/db` folder | No setup, version controllable, easy debugging |
| Testing | pytest | Standard Python testing |
| Real-time | Server-Sent Events (SSE) | Simple push updates for game clock |

---

## Project Structure

```
country-sim-game/
│
├── docs/                          # Documentation (you are here)
│   ├── 01-PROJECT-SETUP.md
│   ├── 02-DATA-MODELS.md
│   ├── 03-MVP-DISPLAY.md
│   ├── 04-GAME-ENGINE-PLAN.md
│   └── 05-TESTING-STRATEGY.md
│
├── db/                            # File-based database
│   ├── countries/                 # Country state files
│   │   ├── ISR.json              # Israel
│   │   ├── USA.json              # United States
│   │   └── ...
│   ├── catalog/                   # Static game data
│   │   ├── weapons_catalog.json  # All weapons in game
│   │   ├── events_catalog.json   # Event definitions
│   │   └── constraints.json      # Rule definitions
│   ├── relations/                 # Bilateral relations
│   │   └── relations_matrix.json
│   └── game_state.json           # Current game meta state
│
├── backend/                       # Python backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   ├── config.py                 # Game configuration
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── country.py            # Country endpoints
│   │   ├── military.py           # Military endpoints
│   │   ├── economy.py            # Economy endpoints
│   │   ├── relations.py          # Relations endpoints
│   │   └── game.py               # Game control (pause, speed)
│   │
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── country.py
│   │   ├── economy.py
│   │   ├── military.py
│   │   ├── workforce.py
│   │   ├── relations.py
│   │   └── events.py
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── db_service.py         # JSON file operations
│   │   ├── country_service.py
│   │   ├── economy_service.py
│   │   ├── military_service.py
│   │   └── clock_service.py      # Game time management
│   │
│   ├── engine/                   # Game engine (Phase 3+)
│   │   ├── __init__.py
│   │   ├── tick_processor.py     # Process game ticks
│   │   ├── constraint_engine.py  # Validate actions
│   │   ├── event_engine.py       # Event probability
│   │   └── calculator.py         # KPI calculations
│   │
│   └── utils/                    # Helpers
│       ├── __init__.py
│       └── helpers.py
│
├── frontend/                      # Static frontend
│   ├── index.html                # Main page
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js                # Main app logic
│   │   ├── api.js                # API client
│   │   ├── clock.js              # Game clock display
│   │   └── components/           # UI components
│   │       ├── dashboard.js
│   │       ├── economy.js
│   │       ├── military.js
│   │       └── relations.js
│   └── assets/
│       └── flags/                # Country flag images
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_models/
│   │   └── test_country.py
│   ├── test_services/
│   │   └── test_db_service.py
│   ├── test_engine/
│   │   ├── test_constraints.py
│   │   ├── test_tick_processor.py
│   │   └── test_events.py
│   └── test_api/
│       └── test_country_api.py
│
├── scripts/                       # Utility scripts
│   ├── seed_database.py          # Initialize DB with real data
│   ├── reset_game.py             # Reset to initial state
│   └── validate_data.py          # Validate JSON schemas
│
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── .gitignore
└── README.md
```

---

## Dependencies

### requirements.txt

```
# API Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Data Validation
pydantic==2.5.3

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0  # For testing FastAPI

# Utilities
python-dateutil==2.8.2
```

---

## Initial Setup Commands

```bash
# Create project directory
mkdir country-sim-game
cd country-sim-game

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p db/{countries,catalog,relations}
mkdir -p backend/{api,models,services,engine,utils}
mkdir -p frontend/{css,js/components,assets/flags}
mkdir -p tests/{test_models,test_services,test_engine,test_api}
mkdir -p scripts docs

# Initialize Python packages
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/services/__init__.py
touch backend/engine/__init__.py
touch backend/utils/__init__.py
touch tests/__init__.py

# Run the application (after implementation)
uvicorn backend.main:app --reload --port 8000
```

---

## Configuration

### backend/config.py

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class GameConfig(BaseSettings):
    # Paths
    DB_PATH: Path = Path("db")
    
    # Game Clock
    REAL_SECONDS_PER_GAME_DAY: float = 1.0  # 1 real second = 1 game day
    GAME_START_YEAR: int = 2024
    
    # Tick Intervals (in game days)
    ECONOMIC_TICK_DAYS: int = 30      # Monthly
    DEMOGRAPHIC_TICK_DAYS: int = 180  # Bi-annually  
    DEVELOPMENT_TICK_DAYS: int = 90   # Quarterly
    POLITICAL_TICK_DAYS: int = 365    # Yearly
    EVENT_CHECK_DAYS: int = 30        # Monthly
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"

config = GameConfig()
```

---

## Git Ignore

### .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# IDE
.idea/
.vscode/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# Game saves (optional - may want to track)
# db/countries/*.json
# db/game_state.json
```

---

## Next Steps

1. **Read**: `02-DATA-MODELS.md` - Understand all data structures
2. **Read**: `03-MVP-DISPLAY.md` - Plan for first visible output
3. **Execute**: Implement MVP display
4. **Read**: `04-GAME-ENGINE-PLAN.md` - Full implementation roadmap
5. **Read**: `05-TESTING-STRATEGY.md` - Testing approach
