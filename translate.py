from transformers import MarianMTModel, MarianTokenizer

# Load the model and tokenizer
model_name = 'Helsinki-NLP/opus-mt-ja-en'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Translate Japanese sentence to English
japanese_text = "これは日本語の文章です。"
translated = model.generate(**tokenizer(japanese_text, return_tensors="pt", padding=True))
english_text = tokenizer.decode(translated[0], skip_special_tokens=True)

print(english_text)
