from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key="AIzaSyDCLq8Y8dDgOrsNIDl-SYBkK1VUPeRJz00")  # paste your key

for model in client.models.list():
    print(model.name)