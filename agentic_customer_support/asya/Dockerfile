# Dockerfile for Asya handlers
# This is a template - adjust based on your Asya runtime image

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler code
COPY handlers/ ./handlers/

# Set handler entrypoint (Asya runtime will call this)
ENV ASYA_HANDLER="handlers.ticket_ingester.process"
ENV PYTHONPATH="/app"

# Asya runtime will execute the handler
CMD ["python", "-m", "asya.runtime"]

