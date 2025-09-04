# Use the official Python 3.13.4 slim image as the base image
FROM python:3.13.4-slim-bullseye

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /code

# Install the application dependencies.
WORKDIR /code

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-cache

# Ensure the script has execute permissions
RUN chmod +x ./scripts/start-backend.sh

# Expose the port your application runs on
EXPOSE 8000

# Run the application.
ENTRYPOINT ["./scripts/start-backend.sh"]