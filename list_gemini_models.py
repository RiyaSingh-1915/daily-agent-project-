# list_gemini_models.py
import os
import google.generativeai as genai

key = os.getenv("GEMINI_API_KEY")
if not key and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS first")

genai.configure(api_key=key)

# different genai versions expose list APIs differently; try common ones
print("Trying to list available models...")

try:
    # newer interface: genai.list_models()
    models = genai.list_models()
    print("genai.list_models() result:")
    for m in models:
        print(m)
except Exception as e:
    # try responses.list_models or genai.get_models
    try:
        if hasattr(genai, "models") and hasattr(genai.models, "list"):
            models = genai.models.list()
            print("genai.models.list() result:")
            for m in models:
                print(m)
        else:
            print("No list_models convenience function found, trying low-level call... Exception:", e)
            raise
    except Exception as e2:
        print("Failed to list models with the available genai library. Exception:", e2)
        # show version information
        import pkgutil, importlib
        mod = importlib.import_module("google.generativeai")
        print("genai module spec:", getattr(mod, "__spec__", None))
        print("genai module file:", getattr(mod, "__file__", None))
        raise
