FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest pytest-timeout

# Create directory structure
RUN mkdir -p src tests

# Copy student code and tests
COPY src/ ./src/
COPY tests/ ./tests/

# Create __init__.py files to make directories into Python packages
RUN touch src/__init__.py tests/__init__.py

# Add current directory to PYTHONPATH so tests can import from src
ENV PYTHONPATH=/app

# Set timeout for tests to prevent infinite loops
ENV PYTEST_TIMEOUT=30

# Run tests and capture output with markers
CMD ["python", "-m", "pytest", "tests/", "-v", "--no-header", "-rA", "--timeout=30"]
