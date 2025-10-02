# Use an official Python runtime as a parent image
FROM python:3.13-slim
ENV PORT=8501
ENV PYTHONPATH=/:/app
# Set the working directory in the container
WORKDIR /app

# Copy the dependency management files
COPY pyproject.toml uv.lock* ./

# Install uv and dependencies
RUN pip install uv
RUN uv sync --no-cache
#--frozen --no-cache
#pip install --system --locked

# Copy the rest of the application code
# COPY app .
# COPY lib agents app/
COPY . .
COPY .streamlit/secrets_forthelife.toml .streamlit/secrets.toml
# Expose the port that Streamlit runs on
EXPOSE ${PORT}

# Define the command to run the app
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["uv","run","streamlit","run","app/Home.py"]
# CMD ["/usr/local/bin/entrypoint.sh"]
