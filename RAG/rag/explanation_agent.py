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

"""Sequential Explanation Agent Module.

This module defines the Sequential Explanation Agent, which orchestrates a three-stage
workflow to provide explanations for student questions based on their board, grade, and subject.

The sequential workflow consists of:
1. Context Extractor Agent: Extracts board, grade, and subject from user query
2. RAG Retrieval Agent: Retrieves relevant content from textbooks in the corpus
3. Explanation Generator Agent: Generates age-appropriate explanations with citations

The SequentialAgent executes these sub-agents in a fixed order, passing data between
them through shared state using output keys.
"""

from google.adk.agents import SequentialAgent

from .agents import (
    create_context_extractor_agent,
    create_explanation_generator_agent,
    create_rag_retrieval_agent,
)


def create_explanation_agent(
    model: str = 'gemini-2.5-flash',
    name: str = 'explanation_agent',
) -> SequentialAgent:
    """Creates and returns a Sequential Explanation Agent.
    
    The Sequential Explanation Agent orchestrates a three-stage workflow:
    
    1. **Context Extractor Agent**: Analyzes the user query to extract:
       - Education Board (e.g., CBSE, ICSE, State Board, IB, etc.)
       - Grade Level (e.g., Grade 10, Class 9, etc.)
       - Subject (e.g., Mathematics, Science, English, etc.)
       Stores this in state['student_context']
    
    2. **RAG Retrieval Agent**: Uses the extracted context to retrieve relevant
       textbook content from the RAG corpus. Constructs targeted queries like:
       "CBSE Grade 10 Science: What is photosynthesis?"
       Stores retrieved content in state['retrieved_content']
    
    3. **Explanation Generator Agent**: Synthesizes the retrieved content into
       clear, age-appropriate explanations tailored to the student's grade level.
       Includes proper citations and stores the final explanation in state['final_explanation']
    
    The SequentialAgent ensures these agents execute in the specified order and
    share the same InvocationContext, allowing data to be passed between stages
    through the shared state.
    
    Args:
        model: The model name to use for all sub-agents. Defaults to 'gemini-2.5-flash'.
        name: The name of the sequential agent. Defaults to 'explanation_agent'.
    
    Returns:
        SequentialAgent: A configured Sequential Explanation Agent instance.
    
    Example:
        >>> agent = create_explanation_agent()
        >>> # The agent will process queries through the three-stage workflow
        >>> # User: "I'm studying CBSE Grade 10 Science. Can you explain photosynthesis?"
        >>> # Agent extracts context, retrieves content, and generates explanation
    
    Note:
        This agent requires the RAG_CORPUS environment variable to be set.
        The RAG agent is specifically designed for retrieving information from
        textbooks in the corpus, not for general knowledge queries.
    """
    # Create sub-agents in the order they will execute
    context_extractor = create_context_extractor_agent(model=model)
    rag_retrieval = create_rag_retrieval_agent(model=model)
    explanation_generator = create_explanation_generator_agent(model=model)
    
    # Create the sequential agent with sub-agents in execution order
    sequential_agent = SequentialAgent(
        name=name,
        description=(
            'Sequential agent that provides explanations for student questions based on '
            'their board, grade, and subject. Executes three stages: context extraction, '
            'RAG retrieval from textbooks, and explanation generation.'
        ),
        sub_agents=[
            context_extractor,
            rag_retrieval,
            explanation_generator,
        ],
    )
    
    return sequential_agent


# Create the default explanation agent instance
explanation_agent = create_explanation_agent()

