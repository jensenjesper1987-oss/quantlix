FROM python:3.12-slim

WORKDIR /app

COPY orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Orchestrator imports api.db, api.models, api.email
COPY api/ ./api/
COPY orchestrator/ ./orchestrator/
COPY pyproject.toml ./

ENV PYTHONPATH=/app
CMD ["python", "-m", "orchestrator.main"]
