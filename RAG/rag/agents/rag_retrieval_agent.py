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

"""RAG Retrieval Agent Module.

This module defines the RAG Retrieval Agent, which is responsible for retrieving
relevant content from student textbooks in the RAG corpus based on the student's
board, grade, and subject.

The agent uses the Vertex AI RAG Retrieval tool to fetch textbook content and
passes it to the explanation generator agent for synthesis.
"""

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from ..prompts.rag_retrieval_prompts import return_instructions_rag_retrieval


def create_rag_retrieval_agent(model: str = 'gemini-2.5-flash') -> Agent:
    """Creates and returns a RAG Retrieval Agent.
    
    The RAG Retrieval Agent uses the Vertex AI RAG Retrieval tool to fetch relevant
    textbook content from the corpus. It reads the student context (board, grade, subject)
    from the previous agent's output and uses it to construct targeted retrieval queries.
    
    Args:
        model: The model name to use for the agent. Defaults to 'gemini-2.5-flash'.
    
    Returns:
        Agent: A configured RAG Retrieval Agent instance with the retrieval tool.
    
    Raises:
        ValueError: If RAG_CORPUS environment variable is not set.
    
    Example:
        >>> agent = create_rag_retrieval_agent()
        >>> # The agent will retrieve textbook content based on student context
    """
    # Build tools list based on RAG_CORPUS availability
    tools = []
    rag_corpus = os.environ.get("RAG_CORPUS")
    
    if not rag_corpus:
        raise ValueError(
            "RAG_CORPUS environment variable is not set. "
            "Please set RAG_CORPUS in your .env file."
        )
    
    # Create the RAG retrieval tool
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name='retrieve_student_textbook_content',
        description=(
            'Use this tool to retrieve relevant content from student textbooks in the RAG corpus. '
            'The corpus contains PDFs organized by education board, grade level, and subject. '
            'When calling this tool, include the student\'s education board, grade, and subject in the query string '
            'to make retrieval more targeted and efficient. '
            'Format your query as: "[board] [grade] [subject]: [student question]" '
            'Example: "CBSE Grade 10 Science: What is photosynthesis?" '
            'This ensures semantic search retrieves content primarily from the correct textbook, '
            'reducing irrelevant results and improving efficiency. '
            'After retrieval, filter the results to use only chunks from files matching the student\'s '
            'board, grade, and subject (check the file display_name or title in the retrieved chunks).'
        ),
        rag_resources=[
            rag.RagResource(
                # RAG corpus containing student textbooks organized by board, grade, and subject
                # e.g. projects/123/locations/us-central1/ragCorpora/456
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=5,  # Reduced from 10 since queries are more targeted with context
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)
    
    agent = Agent(
        name='RagRetrievalAgent',
        model=model,
        instruction=return_instructions_rag_retrieval(),
        description=(
            'Retrieves relevant textbook content from the RAG corpus based on student context. '
            'Uses the student\'s board, grade, and subject to construct targeted retrieval queries.'
        ),
        tools=tools,
        output_key='retrieved_content',  # Stores retrieved content in state['retrieved_content']
    )
    
    return agent

