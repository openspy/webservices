FROM alpine:3.7
WORKDIR /app
RUN apk add --no-cache \
        uwsgi-python3 \
        python3
COPY . /app

CMD [ "/bin/sh", "run.sh" ]