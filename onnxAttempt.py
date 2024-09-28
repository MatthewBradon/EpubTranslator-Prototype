import torch
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from onnxruntime import InferenceSession, SessionOptions, get_available_providers


print(torch.cuda.is_available())  # Should return True if CUDA is available


# Path to the directory containing the ONNX models and config files
model_path = 'onnx-model-dir'

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en')

# Tokenize the text
text = 'こんにちは、元気ですか？'
inputs = tokenizer(text, return_tensors='pt')

# Check if CUDA is available for ONNX Runtime
if 'CUDAExecutionProvider' in get_available_providers():
    provider = 'CUDAExecutionProvider'
else:
    provider = 'CPUExecutionProvider'
    print("CUDA not available, falling back to CPU.")
# provider = 'CPUExecutionProvider'
# Load the ONNX Seq2Seq model with the specified provider (CUDA or CPU)
model = ORTModelForSeq2SeqLM.from_pretrained(model_path, provider=provider)

# Generate the translated text using the ONNX model
outputs = model.generate(inputs['input_ids'])

# Decode the output
output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(output_text)
