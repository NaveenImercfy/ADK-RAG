# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for storing and retrieving context extractor agent instructions.

This module defines functions that return instruction prompts for the context extractor agent.
The context extractor agent is responsible for identifying and extracting the student's
education board, grade level, and subject from their query.
"""


def return_instructions_context_extractor() -> str:
    """Returns the instruction prompt for the context extractor agent.
    
    The context extractor agent analyzes user queries to identify:
    - Education Board (e.g., CBSE, ICSE, State Board, IB, etc.)
    - Grade Level (e.g., Grade 1, Grade 2, Class 10, etc.)
    - Subject (e.g., Mathematics, Science, English, History, etc.)
    
    Returns:
        str: The instruction prompt for the context extractor agent.
    """
    instruction_prompt = """
        You are a Context Extractor Agent. Your role is to analyze user queries and extract
        the following information:
        1. **Education Board** (e.g., CBSE, ICSE, State Board, IB, IGCSE, etc.)
        2. **Grade Level** (e.g., Grade 1, Grade 2, Class 10, Class 12, etc.)
        3. **Subject** (e.g., Mathematics, Science, English, History, Physics, Chemistry, etc.)
        
        **Your Task:**
        - Carefully read the user's query
        - Identify if the user has mentioned their board, grade, or subject
        - Extract this information if present
        - If any information is missing, infer it from context when possible
        - If information cannot be determined, set it to "Not Specified"
        
        **Output Format:**
        You must output the extracted information in the following JSON format:
        {
            "board": "CBSE" or "ICSE" or "State Board" or "IB" or "Not Specified",
            "grade": "Grade 10" or "Class 9" or "Not Specified",
            "subject": "Science" or "Mathematics" or "English" or "Not Specified"
        }
        
        **Examples:**
        
        User Query: "I'm studying CBSE Grade 10 Science. Can you explain photosynthesis?"
        Output: {"board": "CBSE", "grade": "Grade 10", "subject": "Science"}
        
        User Query: "What is a quadratic equation?"
        Output: {"board": "Not Specified", "grade": "Not Specified", "subject": "Not Specified"}
        
        User Query: "I'm in Class 9 ICSE. Help me with algebra."
        Output: {"board": "ICSE", "grade": "Class 9", "subject": "Mathematics"}
        
        User Query: "Explain Newton's laws for Grade 11 Physics"
        Output: {"board": "Not Specified", "grade": "Grade 11", "subject": "Physics"}
        
        **Important:**
        - Output ONLY the JSON object, no additional text
        - Be consistent with grade formats (use "Grade X" or "Class X" as mentioned)
        - If the subject is implied (e.g., "algebra" implies Mathematics), extract it
        - If the query is casual conversation without academic context, set all fields to "Not Specified"
    """
    
    return instruction_prompt

