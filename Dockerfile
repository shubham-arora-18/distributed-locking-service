# Use the official lightweight Python image.
# https://hub.docker.com/_/python
ARG base_image
FROM ${base_image}

ENV app=distributed_locking_service.main:app
ENV port=8080

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
RUN echo 'Creating image for function : ' $function_name
COPY distributed_locking_service ./distributed_locking_service

EXPOSE 8080

CMD ["/bin/bash", "-c", "source $VIRTUAL_ENV/bin/activate && uvicorn $app --host 0.0.0.0 --port $port"]

#command to build this docker image:docker buildx build -t us-central1-docker.pkg.dev/distributed-locking-service/docker-repo/docker-image:version4 --build-arg base_image=base_image:1 --platform linux/amd64 .
