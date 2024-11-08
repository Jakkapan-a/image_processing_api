FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime
ARG DEBIAN_FRONTEND=noninteractive
ARG TEST_ENV

WORKDIR /app

RUN conda update conda -y

RUN --mount=type=cache,target="/var/cache/apt",sharing=locked \
    --mount=type=cache,target="/var/lib/apt/lists",sharing=locked \
    apt-get -y update \
    && apt-get install -y git \
    && apt-get install -y wget \
    && apt-get install -y g++ freeglut3-dev build-essential libx11-dev \
    libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev libfreeimage-dev \
    && apt-get -y install ffmpeg libsm6 libxext6 libffi-dev python3-dev python3-pip gcc

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_CACHE_DIR=/.cache \
    PORT=10010 \
    WORKERS=2 \
    THREADS=4 \
    CUDA_HOME=/usr/local/cuda

#RUN conda install -c "nvidia/label/cuda-12.1.1" cuda -y
RUN conda install -c "nvidia/label/cuda-12.1" cuda -y
ENV CUDA_HOME=/opt/conda \
    TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6+PTX;8.9;9.0"

COPY requirements.txt .
RUN --mount=type=cache,target=${PIP_CACHE_DIR},sharing=locked \
    pip3 install -r requirements.txt

WORKDIR /app

COPY . ./

COPY tests /app/tests

# Download the YOLO models
RUN /bin/sh -c 'if [ ! -f /app/models/detect/yolov8m.pt ]; then \
    yolo predict model=/app/models/detect/yolov8m.pt source=/app/tests/car.jpg \
    && yolo predict model=/app/models/detect/yolov8n.pt source=/app/tests/car.jpg \
    && yolo predict model=/app/models/detect/yolov8n-cls.pt source=/app/tests/car.jpg \
    && yolo predict model=/app/models/detect/yolov8n-seg.pt source=/app/tests/car.jpg; \
    fi'

ENV PYTHONPATH=/app

# Change permissions
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]