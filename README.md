# Country Simulation Game

A single-player country simulation game combining city-builder economics (SimCity), grand strategy depth (Victoria), and military realism (Red Alert). Players manage real countries with real-ish data, making decisions that ripple through interconnected systems.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000/static/index.html in your browser.

## Project Structure

See [docs/01-PROJECT-SETUP.md](docs/01-PROJECT-SETUP.md) for full documentation.

## Testing

```bash
pytest
```
