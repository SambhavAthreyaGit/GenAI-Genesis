# GenAI-Genesis sandbox: KiCad CLI + Python for schematic/PCB generation and ERC.
# Uses official KiCad image for kicad-cli; adds Python and runner.
FROM kicad/kicad:8.0

# Install Python 3 and pip (Debian/Ubuntu in KiCad image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY spec_schema.py runner.py ./

# Contract: backend mounts work dir at /work with input/spec.json and expects output in /work/output
# We run as non-root; ensure we can write to /work
ENV WORK=/work
RUN mkdir -p /work/input /work/output && chmod -R 777 /work

# Entry: run generator (reads /work/input/spec.json, writes to /work/output/)
CMD ["python3", "runner.py"]
