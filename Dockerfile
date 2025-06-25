FROM python:3.12-slim
ARG DAGSTER_APP="not_set"

RUN if [ "$DAGSTER_APP" = "not_set" ]; then echo "ERROR: DAGSTER_APP must be set" && exit 1; fi

# install poetry
RUN apt-get update && apt-get install -y pipx
RUN pipx install poetry

# add poetry to path
ENV PATH="/root/.local/bin:$PATH"

COPY ./${DAGSTER_APP} /app
COPY workspace.yaml /

WORKDIR /app
RUN poetry install

EXPOSE 4000
CMD ["./start.sh"]
