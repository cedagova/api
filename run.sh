#!/bin/bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-9000}

