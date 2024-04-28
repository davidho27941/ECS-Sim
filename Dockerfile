FROM python:3.10 as base
ENV DEBIAN_FRONTEND=noninteractive

RUN <<EOF
apt update -y
apt install -y vim ranger build-essential wget curl
mkdir /root/ecs_sim
pip install uv

uv pip install --python=$(which python) simpy numpy pandas
EOF

WORKDIR /root/workplace
