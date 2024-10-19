from optimum.onnxruntime import ORTModelForSeq2SeqLM
from onnxruntime import InferenceSession, SessionOptions, get_available_providers
from transformers import AutoTokenizer, MarianTokenizer

text = '実は、「小説家になろう」というサイトにてさい載れん連をしていたこの作品なのですが、このたび度スニーカー文庫さんに声をかけて頂き、せき籍しよ書化の運びとなりました。'
tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en')
inputs = tokenizer(text, return_tensors='pt')
modelPath = 'onnx-model-dir'
model = ORTModelForSeq2SeqLM.from_pretrained(modelPath)
generated = model.generate(**inputs)
print(tokenizer.decode(generated[0], skip_special_tokens=True))

