from fastapi import FastAPI
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"message": "FastAPI GPT endpoint is up!"}

@app.get("/ask")
def ask_gpt():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return {"gpt_response": response.choices[0].message["content"]}
    except Exception as e:
        return {"error": str(e)}
