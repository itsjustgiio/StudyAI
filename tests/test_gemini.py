from app.integrations import gemini_api

result = gemini_api.generate_text("Summarize: The mitochondria is the powerhouse of the cell.")
print(result)
