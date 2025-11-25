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

"""Explanation Generator Agent Module.

This module defines the Explanation Generator Agent, which synthesizes retrieved
textbook content into clear, age-appropriate explanations tailored to the student's
grade level.

The agent reads the student context and retrieved content from previous agents and
generates curriculum-aligned explanations with proper citations.
"""

from google.adk.agents import Agent

from ..prompts.explanation_generator_prompts import return_instructions_explanation_generator


def create_explanation_generator_agent(model: str = 'gemini-2.5-flash') -> Agent:
    """Creates and returns an Explanation Generator Agent.
    
    The Explanation Generator Agent synthesizes retrieved textbook content into
    clear, engaging, and age-appropriate explanations. It reads the student context
    (board, grade, subject) and retrieved content from previous agents in the workflow
    and generates curriculum-aligned explanations with proper citations.
    
    Args:
        model: The model name to use for the agent. Defaults to 'gemini-2.5-flash'.
    
    Returns:
        Agent: A configured Explanation Generator Agent instance.
    
    Example:
        >>> agent = create_explanation_generator_agent()
        >>> # The agent will generate explanations based on student context and retrieved content
    """
    agent = Agent(
        name='ExplanationGeneratorAgent',
        model=model,
        instruction=return_instructions_explanation_generator(),
        description=(
            'Generates age-appropriate, curriculum-aligned explanations based on '
            'retrieved textbook content and student context (board, grade, subject). '
            'Includes proper citations and tailors explanations to the student\'s grade level.'
        ),
        output_key='final_explanation',  # Stores final explanation in state['final_explanation']
    )
    
    return agent

