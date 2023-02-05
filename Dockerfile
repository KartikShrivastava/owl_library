FROM python:3.8-slim-buster AS builder

# stage 1 get python and install additional dependencies to build postgres
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
    
# stage 2 install project dependencies in virtual environment
RUN python -m venv /opt/venv
# activate venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt

# stage 3 keep project dependencies(how?) and remove gcc and other dependencies
FROM python:3.8-slim-buster
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY . .
