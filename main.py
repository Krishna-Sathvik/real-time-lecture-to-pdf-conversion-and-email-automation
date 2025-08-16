import google.generativeai as genai

genai.configure(api_key="AIzaSyDQLyCZjLZmP0uWO_WaZVdPIr-gZLmTDy0")
models = genai.list_models()

for model in models:
    print(model.name)
