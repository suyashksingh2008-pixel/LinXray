import PIL.Image
from google import genai

# 1. Connect to the AI (replace with your fresh API key)
client = genai.Client(api_key='')

# 2. Load the screenshot captured by your Playwright sandbox
# Make sure you have an image named 'screenshot.png' in your folder
screenshot = PIL.Image.open(r"C:\Users\xx\OneDrive\Desktop\screenshot.png.png")


prompt = """
You are a senior Cyber Threat Intelligence analyst. 
Examine this screenshot of a potentially malicious website. 
Provide a detailed security report that identifies:
1. Deceptive UI elements (e.g., fake brand logos, disguised buttons).
2. Phishing indicators (e.g., suspicious login forms).
3. An overall risk assessment based on the visual evidence.
"""

print("Analyzing image...\n")


response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=[prompt, screenshot]
)

print("--- VISUAL SECURITY REPORT ---")
print(response.text)
