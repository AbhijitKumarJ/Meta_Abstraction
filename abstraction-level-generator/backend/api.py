# backend/api.py

import asyncio
import aiohttp
import json
import time
import os
from fastapi import APIRouter, HTTPException
from models import Question, AbstractionResponse, AbstractionLevel, APIResponse
from database import get_db_connection
from typing import List
from improved_api_prompt import generate_prompt

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('GROQ_API_KEY')
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_MODEL = os.environ.get('GROQ_MODEL', "llama-3.1-8b-instant")

router = APIRouter()

MAX_LEVELS = 2
MAX_REQUESTS_PER_MINUTE = 10
request_timestamps: List[float] = []

async def make_api_call(session: aiohttp.ClientSession, prompt: str, level: int) -> str:
    
    # Implement rate limiting
    current_time = time.time()
    request_timestamps.append(current_time)
    if len(request_timestamps) > MAX_REQUESTS_PER_MINUTE:
        oldest_timestamp = request_timestamps.pop(0)
        if current_time - oldest_timestamp < 60:
            await asyncio.sleep(60 - (current_time - oldest_timestamp))

    # headers = {
    #     "Authorization": f"Bearer {API_KEY}",
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     # "model": API_MODEL,
    #     # "prompt": prompt,
    #     # "max_tokens": 150
        
    #     "model":API_MODEL,
    #     "messages":[
    #         {
    #             "role": "user",
    #             "content": prompt #"Generate abstraction level 0 for: A jar contains buttons of four different colours. There are twice as many yellow as green, twice as many red as yellow, and twice as many blue as red. What is the probability of taking from the jar: a blue button; a red button; a yellow button; a green button? You may assume that you are only taking one button at a time and replacing it in the jar before selecting the next one."
    #         }
    #     ],
    #     "temperature":0.3,
    #     "max_tokens":8192,
    #     "top_p":1,
    #     "stream":False,
    #     "stop":None,
    # }

    try:
        from groq import Groq

        client = Groq(api_key=API_KEY)
        completion = client.chat.completions.create(
            model= API_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt #"Generate abstraction level 0 for: A jar contains buttons of four different colours. There are twice as many yellow as green, twice as many red as yellow, and twice as many blue as red. What is the probability of taking from the jar: a blue button; a red button; a yellow button; a green button? You may assume that you are only taking one button at a time and replacing it in the jar before selecting the next one."
                }
            ],
            temperature=0.3,
            max_tokens=7992,
            top_p=1,
            stream=False,
            stop=None,
        )

        return completion.choices[0].message.content

        # async with session.post(API_URL, headers=headers, json=data) as response:
        #     result = await response.json()
        #     api_response = APIResponse(**result)
        #     return api_response.choices[0]["text"].strip()
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
            # In your API call function
            prompt = generate_prompt(question.raw_question, level)
            try:
                response = await make_api_call(session, prompt, level)
                # Parse response and extract required information
                # This is a simplified version and might need adjustment based on the actual API response
                parsed_response = json.loads(response)
                abstraction = AbstractionLevel(
                    level_number=level,
                    ideal_representation=parsed_response['ideal_representation'],
                    generated_question=parsed_response['generated_question'],
                    score=parsed_response['score'],
                    variables=parsed_response['variables']
                )
                levels.append(abstraction)

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Log raw response
                    cursor.execute("""
                        INSERT INTO RawRequestResponseLog 
                        (question_id, level_number, request_type, input_prompt, raw_response, status) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (question_id, level, 'abstraction', prompt, response, 'success'))

                    # Log detailed abstraction
                    cursor.execute("""
                        INSERT INTO DetailedAbstractions 
                        (question_id, level_number, ideal_representation, generated_question, score, variables) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (question_id, level, abstraction.ideal_representation, abstraction.generated_question, 
                          abstraction.score, json.dumps(abstraction.variables)))

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
