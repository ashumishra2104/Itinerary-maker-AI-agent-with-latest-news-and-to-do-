import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key found")
    exit()

client = genai.Client(api_key=api_key)

try:
    print("Attempting to generate image with google-genai...")
    response = client.models.generate_images(
        model='imagen-3.0-generate-001',
        prompt='A futuristic banana city',
        config=types.GenerateImagesConfig(
            number_of_images=1,
        )
    )
    if response.generated_images:
        print("Success! Image generated.")
        # response.generated_images[0].image.save("test_genai.png")
    else:
        print("No images returned.")

except Exception as e:
    print(f"Error: {e}")
