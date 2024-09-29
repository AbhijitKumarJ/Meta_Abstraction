# backend/api.py

import asyncio
import aiohttp
import json
import time
import os
from fastapi import APIRouter, HTTPException
from models import Question, AbstractionResponse, AbstractionLevel, APIResponse
from database import get_db_connection
from typing import List, Deque
from collections import deque
from improved_api_prompt import generate_prompt

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('GROQ_API_KEY')
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_MODEL = os.environ.get('GROQ_MODEL', "llama-3.1-8b-instant")

router = APIRouter()

MAX_LEVELS = 2
MAX_REQUESTS_PER_MINUTE = 10
request_timestamps: Deque[float] = deque()  # Use a deque for efficient queue operations

async def make_api_call(session: aiohttp.ClientSession, prompt: str, level: int) -> str:
    
    # Implement rate limiting
    current_time = time.time()
    request_timestamps.append(current_time)
    if len(request_timestamps) > MAX_REQUESTS_PER_MINUTE:
        oldest_timestamp = request_timestamps.popleft()
        if current_time - oldest_timestamp < 60:
            await asyncio.sleep(60 - (current_time - oldest_timestamp))

    try:
        from groq import Groq

        client = Groq(api_key=API_KEY)
        completion = client.chat.completions.create(
            model= API_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=7992,  # Reduced from potentially incorrect 8192. Consider adjusting as needed.
            top_p=1,
            stream=False,
            stop=None,
        )

        return completion.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")

@router.post("/generate_abstractions/", response_model=AbstractionResponse)
async def generate_abstractions(question: Question):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Questions (raw_question) VALUES (?)", (question.raw_question,))
        question_id = cursor.lastrowid
        conn.commit()

    levels = []
    async with aiohttp.ClientSession() as session:
        for level in range(MAX_LEVELS):
            prompt = generate_prompt(question.raw_question, level)
            try:
                response_content = await make_api_call(session, prompt, level)

                try:
                    # Attempt to parse the response as JSON
                    parsed_response = json.loads(response_content)
                except json.JSONDecodeError:
                    # Handle cases where the response isn't valid JSON.  This may require further debugging and refinement based on the actual API behavior.
                    raise HTTPException(status_code=500, detail=f"Invalid JSON response from API: {response_content}")


                abstraction = AbstractionLevel(
                    level_number=level,
                    ideal_representation=parsed_response['ideal_representation'],
                    generated_question=parsed_response['generated_question'],
                    score=parsed_response['score'],
                    variables=parsed_response['variables']
                )
                levels.append(abstraction)

                # ... (database logging code remains unchanged)

            except Exception as e:
                # ... (error handling and logging code remains unchanged)

    return AbstractionResponse(question_id=question_id, levels=levels)
