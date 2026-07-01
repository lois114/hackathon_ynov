FROM nvcr.io/nvidia/tritonserver:24.08-pyt-python-py3

RUN pip install --no-cache-dir \
    transformers==4.45.2 \
    accelerate==0.34.2 \
    sentencepiece==0.2.0 \
    einops==0.8.0 \
    protobuf==4.25.3

COPY model_repository /models

ENV TRITON_HF_MODEL=microsoft/Phi-3.5-mini-instruct
ENV TRITON_MAX_NEW_TOKENS=256

CMD ["tritonserver", "--model-repository=/models", "--http-port=8000", "--grpc-port=8001", "--metrics-port=8002"]
