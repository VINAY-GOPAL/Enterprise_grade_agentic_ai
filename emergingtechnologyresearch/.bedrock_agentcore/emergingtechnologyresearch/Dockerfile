FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1

RUN uv pip install \
    crewai \
    boto3 \
    langfuse \
    openinference-instrumentation-crewai \
    openinference-instrumentation-litellm \
    bedrock-agentcore==1.3.1 \
    bedrock-agentcore-starter-toolkit==0.2.0 \
    python-dotenv \
    pydantic

RUN uv pip install aws-opentelemetry-distro==0.12.2

ENV DOCKER_CONTAINER=1

RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

COPY . .

CMD ["opentelemetry-instrument", "python", "-m", "agentcore"]