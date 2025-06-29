# AI Trading Backend with GPU Acceleration

This directory contains the backend implementation for the AI Trading App with GPU acceleration support.

## Prerequisites

- Node.js 14+ for the API server
- Python 3.8+ for the AI training
- NVIDIA GPU with CUDA support (optional but recommended)
- NVIDIA CUDA Toolkit 11.0+ (required for GPU acceleration)
- NVIDIA cuDNN 8.0+ (required for GPU acceleration)

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

For GPU support, make sure you have installed PyTorch with CUDA:

```bash
# For CUDA 11.6
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
```

### 2. Install Node.js dependencies

```bash
npm install
```

### 3. Verify GPU support

To verify that your GPU is properly detected by PyTorch, run:

```bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available()); print('GPU Count:', torch.cuda.device_count()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

## Starting the Server

Start the backend API server:

```bash
npm start
```

The server should start on port 3000 by default. You can change this by setting the PORT environment variable.

## API Endpoints

- `POST /api/ai/training/start` - Start a new AI training job
  - Parameters:
    - `model_type` (string): Type of model to train
    - `parameters` (object): Training parameters
    - `use_gpu` (boolean): Whether to use GPU acceleration
  
- `POST /api/ai/training/stop` - Stop a running training job
  - Parameters:
    - `job_id` (string): ID of the job to stop
  
- `GET /api/ai/training/progress` - Get the progress of a training job
  - Query parameters:
    - `model_type` (string): Type of model to check

## Troubleshooting

### GPU Not Detected

If your GPU is not detected:

1. Make sure you have installed the NVIDIA GPU drivers
2. Install CUDA Toolkit matching your PyTorch version
3. Verify CUDA installation with `nvidia-smi` command
4. Check that PyTorch was installed with CUDA support

### Training Performance

With GPU acceleration, training should be significantly faster (typically 5-10x faster depending on your GPU model).

If you don't see a performance improvement:
1. Check GPU utilization during training with `nvidia-smi -l 1`
2. Verify CUDA is properly installed and detected by PyTorch
3. Try with a different batch size, which can affect GPU utilization 
