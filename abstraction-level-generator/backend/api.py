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

MAX_LEVELS = 4
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

                    # Parse the 'variables' field into a dictionary
                    try:
                        variables = parsed_response['variables'] #json.loads(parsed_response['variables'])
                    except (KeyError, TypeError, json.JSONDecodeError):
                        variables = '' #{}  # Or handle the error as needed, e.g., set a default value

                except json.JSONDecodeError:
                    # Handle cases where the response isn't valid JSON.
                    raise HTTPException(status_code=500, detail=f"Invalid JSON response from API: {response_content}")


                abstraction = AbstractionLevel(
                    level_number=level,
                    ideal_representation=parsed_response['ideal_representation'],
                    generated_question=parsed_response['generated_question'],
                    score=parsed_response['score'],
                    variables=variables # Assign the parsed variables dictionary
                )
                levels.append(abstraction)

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Log raw response
                    cursor.execute("""
                        INSERT INTO RawRequestResponseLog 
                        (question_id, level_number, request_type, input_prompt, raw_response, status) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (question_id, level, 'abstraction', prompt, response_content, 'success'))

                    # Log detailed abstraction
                    cursor.execute("""
                        INSERT INTO DetailedAbstractions 
                        (question_id, level_number, ideal_representation, generated_question, score, variables) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (question_id, level, abstraction.ideal_representation, abstraction.generated_question, 
                          abstraction.score, abstraction.variables))

                    conn.commit()

            except Exception as e:
                # Log error
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO RawRequestResponseLog 
                        (question_id, level_number, request_type, input_prompt, raw_response, status) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (question_id, level, 'abstraction', prompt, str(e), 'failure'))
                    conn.commit()

    return AbstractionResponse(question_id=question_id, levels=levels)
