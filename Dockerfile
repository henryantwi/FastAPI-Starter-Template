FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Ensure the script has execute permissions
RUN chmod +x ./scripts/entrypoint.sh

# Expose the port your application runs on
EXPOSE 8000

# Run the application.
ENTRYPOINT ["./scripts/entrypoint.sh"]