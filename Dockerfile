FROM python:3.12-slim
ARG DAGSTER_APP="not_set"

RUN if [ "$DAGSTER_APP" = "not_set" ]; then echo "ERROR: DAGSTER_APP must be set" && exit 1; fi

# install poetry
RUN apt-get update && apt-get install -y pipx
RUN pipx install poetry

# add poetry to path
ENV PATH="/root/.local/bin:$PATH"

# set up dagster home and config
RUN mkdir /dagster
ENV DAGSTER_HOME=/dagster
COPY dagster.yaml /dagster/dagster.yaml

COPY ./${DAGSTER_APP} /app
COPY workspace.yaml /

WORKDIR /app
RUN poetry config virtualenvs.in-project true && poetry install
RUN chmod +x ./start.sh

# Add the virtualenv bin to PATH so dagster command is available
ENV PATH="/app/.venv/bin:$PATH"

CMD ["./start.sh"]
