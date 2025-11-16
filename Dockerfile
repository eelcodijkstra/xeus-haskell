FROM mambaorg/micromamba:ubuntu

COPY --from=busybox:musl /bin/busybox /bin/busybox

USER root
RUN chmod 777 -R /usr/local

USER $MAMBA_USER
COPY --chown=$MAMBA_USER:$MAMBA_USER ./environment-dev.yml /tmp/environment-dev.yml
COPY --chown=$MAMBA_USER:$MAMBA_USER ./environment-wasm-build.yml /tmp/environment-wasm-build.yml
COPY --chown=$MAMBA_USER:$MAMBA_USER ./environment-wasm-host.yml /tmp/environment-wasm-host.yml
RUN micromamba install -y -n base -f /tmp/environment-dev.yml && \
    micromamba env create -y -f /tmp/environment-wasm-build.yml && \
    micromamba create -y -f /tmp/environment-wasm-host.yml --platform=emscripten-wasm32 && \
    micromamba clean --all --yes

COPY --chown=$MAMBA_USER:$MAMBA_USER <<-EOF /usr/local/bin/runs
#!/bin/bash
set -e
for cmd in "\$@"; do
  bash -c "\$cmd"
done
EOF

RUN chmod +x /usr/local/bin/runs

WORKDIR /work
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "runs", "cp -vR /host/* /work", "cmake -B /tmp /work", "cmake --build /tmp", "cmake --install /tmp"]
CMD ["pytest"]
