from llm_clients.gemini_client import GeminiClient
c = GeminiClient()
resp = c.generate("Say hello", max_tokens=20)
print("Gemini test successful:", resp.text)
