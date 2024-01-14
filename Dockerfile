FROM python:3.10-slim

ARG function_name
ARG app_name
ENV app=$app_name

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
ENV PORT 8080

RUN echo 'Creating image for function : $function_name'

# Not sure if follwing is needed or not.
RUN mkdir build
COPY cicd-tools/build/shared/install_packages.sh ./build/.
RUN ./build/install_packages.sh

# Create new user which will be used for all activities.
RUN groupadd --gid 2000 appgroup && useradd --home-dir /home/appuser --create-home --uid 2000 --gid 2000 --shell /bin/bash --skel /dev/null appuser
RUN chown -R appuser:appgroup /app

USER appuser
SHELL ["bash", "-c"]

# Create virtual environment
ENV VIRTUAL_ENV=/home/appuser/venv
RUN python -m venv $VIRTUAL_ENV

# Installing dependencies
COPY $function_name ./$function_name
COPY pyproject.toml ./
COPY README.md ./
COPY cicd-tools/build/shared/install_proj_requirements.sh ./build/.
RUN source $VIRTUAL_ENV/bin/activate && ./build/install_proj_requirements.sh

RUN mkdir runtime
COPY cicd-tools/runtime/cloud/python_entrypoint.sh runtime/.
CMD ["/bin/bash", "-c", "source $VIRTUAL_ENV/bin/activate && ./runtime/python_entrypoint.sh uvicorn ${app} $PORT"]
