# Minimal image for the migrated Actor Mesh handlers.
# Asya operator mounts /opt/asya/asya_runtime.py and sets ASYA_HANDLER.

FROM python:3.12-slim

WORKDIR /app

# Install runtime deps here if needed (left empty for now to keep image slim)
# COPY tinkering_with_asya/merge_actor_mesh_into_asya/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY ./handlers ./handlers

ENV PYTHONPATH=/app
