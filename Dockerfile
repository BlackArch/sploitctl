FROM python:buster

LABEL version="3.0.2-dev" \
    author="Author BlackArch (https://github.com/BlackArch)" \
    docker_build="docker build -t blackarch/sploitctl:3.0.2-dev ." \
    docker_run_basic="docker run --rm blackarch/sploitctl:3.0.2-dev -H"

COPY [".", "/sploitctl"]

ENV PATH=${PATH}:/sploitctl

RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libgit2-dev && \
    pip install -r /sploitctl/requirements.txt && \
    addgroup sploitctl && \
    useradd -g sploitctl -d /sploitctl -s /bin/sh sploitctl && \
    chown -R sploitctl:sploitctl /sploitctl && \
    export RANDOM_PASSWORD=$(tr -dc A-Za-z0-9 </dev/urandom | head -c44) && \
    echo "root:$RANDOM_PASSWORD" | chpasswd && \
    unset RANDOM_PASSWORD && \
    passwd -l root

USER sploitctl

ENTRYPOINT ["sploitctl.py"]

CMD ["-h"]
