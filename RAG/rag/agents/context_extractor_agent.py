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

"""Context Extractor Agent Module.

This module defines the Context Extractor Agent, which is responsible for extracting
the student's education board, grade level, and subject from their query.

The agent analyzes user queries to identify:
- Education Board (e.g., CBSE, ICSE, State Board, IB, etc.)
- Grade Level (e.g., Grade 1, Grade 2, Class 10, etc.)
- Subject (e.g., Mathematics, Science, English, History, etc.)

This information is then passed to subsequent agents in the sequential workflow.
"""

from google.adk.agents import Agent

from ..prompts.context_extractor_prompts import return_instructions_context_extractor


def create_context_extractor_agent(model: str = 'gemini-2.5-flash') -> Agent:
    """Creates and returns a Context Extractor Agent.
    
    The Context Extractor Agent is an LLM agent that analyzes user queries to extract
    education board, grade level, and subject information. This information is stored
    in the agent's output key for use by subsequent agents in the sequential workflow.
    
    Args:
        model: The model name to use for the agent. Defaults to 'gemini-2.5-flash'.
    
    Returns:
        Agent: A configured Context Extractor Agent instance.
    
    Example:
        >>> agent = create_context_extractor_agent()
        >>> # The agent will extract context from user queries and store it in state
    """
    agent = Agent(
        name='ContextExtractorAgent',
        model=model,
        instruction=return_instructions_context_extractor(),
        description=(
            'Extracts education board, grade level, and subject from user queries. '
            'Outputs structured JSON with board, grade, and subject information.'
        ),
        output_key='student_context',  # Stores extracted context in state['student_context']
    )
    
    return agent

