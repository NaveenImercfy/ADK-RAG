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

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

load_dotenv()

# Build tools list conditionally based on RAG_CORPUS availability
tools = []
rag_corpus = os.environ.get("RAG_CORPUS")

if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name='retrieve_student_textbook_content',
        description=(
            'Use this tool to retrieve relevant content from student textbooks in the RAG corpus. '
            'The corpus contains PDFs organized by education board, grade level, and subject. '
            'IMPORTANT: When calling this tool, you MUST include the student\'s education board, '
            'grade, and subject in the query string to make retrieval more targeted and efficient. '
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

root_agent = Agent(
    model='gemini-2.5-flash',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=tools,
)
