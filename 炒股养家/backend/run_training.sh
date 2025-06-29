#!/bin/bash

# AI Training Runner Script
# This script runs the AI training backend with GPU acceleration

# Get arguments
MODEL_TYPE="$1"
EPOCHS="$2"
LEARNING_RATE="$3"
BATCH_SIZE="$4"
GPU_FLAG="$5"

# Set defaults if not provided
if [ -z "$MODEL_TYPE" ]; then
  MODEL_TYPE="price_prediction"
fi

if [ -z "$EPOCHS" ]; then
  EPOCHS=50
fi

if [ -z "$LEARNING_RATE" ]; then
  LEARNING_RATE=0.001
fi

if [ -z "$BATCH_SIZE" ]; then
  BATCH_SIZE=32
fi

# Check if GPU flag is set
GPU_ARG=""
if [ "$GPU_FLAG" = "true" ]; then
  GPU_ARG="--gpu"
  echo "Using GPU acceleration"
else
  echo "Using CPU only"
fi

# Create JSON parameters
PARAMS="{\"epochs\": $EPOCHS, \"learning_rate\": $LEARNING_RATE, \"batch_size\": $BATCH_SIZE, \"use_gpu\": $([ "$GPU_FLAG" = "true" ] && echo "true" || echo "false")}"

echo "Starting AI training for model: $MODEL_TYPE"
echo "Parameters: $PARAMS"

# Create models directory if it doesn't exist
mkdir -p models

# Run the Python script
python ai_trainer.py --model "$MODEL_TYPE" --params "$PARAMS" $GPU_ARG

# Check if training was successful
if [ $? -eq 0 ]; then
  echo "Training completed successfully"
else
  echo "Training failed"
  exit 1
fi 