FROM python:3.8-slim

COPY --from=apache/beam_python3.8_sdk:2.39.0 /opt/apache/beam /opt/apache_beam

COPY . /beam/
WORKDIR /beam
RUN python -m pip install -r requirements.txt

ENTRYPOINT ["/opt/apache/beam/boot"]
