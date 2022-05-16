FROM alpine:3.9.6

RUN apk --update-cache add \
    python3 \
    python3-dev \
    py3-pip \
    bash \
    build-base \
    linux-headers \
    && pip3 install --upgrade pip \
    && pip3 install \
    tweepy==3.10.0 \
    discord \
    aiohttp \
    asyncio

COPY app.py /app.py
WORKDIR /

ENTRYPOINT ["python3", "/app.py"]