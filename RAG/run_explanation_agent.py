#!/usr/bin/env python3
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

"""Runner script for the Sequential Explanation Agent.

This script provides an alternative way to run the explanation agent
programmatically using the InMemoryRunner.
"""

import os
import sys

from dotenv import load_dotenv
from google.adk.runner import InMemoryRunner

# Load environment variables
load_dotenv()

# Import the explanation agent
from rag.explanation_agent import explanation_agent


def main():
    """Run the explanation agent interactively."""
    print("=" * 60)
    print("Sequential Explanation Agent")
    print("=" * 60)
    print("\nThis agent provides explanations for student questions")
    print("based on their board, grade, and subject.")
    print("\nExample query: I'm studying CBSE Grade 10 Science. Can you explain photosynthesis?")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    # Create runner
    runner = InMemoryRunner(explanation_agent, "explanation_agent")
    
    # Create a session
    session = runner.session_service().create_session("explanation_agent", "user_123")
    print(f"Session created: {session.id()}\n")
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_query = input("You: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_query:
                continue
            
            print("\nAgent: ", end="", flush=True)
            
            # Run the agent
            response_stream = runner.run_async(
                "user_123",
                session.id(),
                user_query
            )
            
            # Stream the response
            full_response = ""
            for event in response_stream:
                if hasattr(event, 'content') and event.content:
                    content = str(event.content)
                    if content:
                        print(content, end="", flush=True)
                        full_response += content
                elif hasattr(event, 'stringify_content'):
                    content = event.stringify_content()
                    if content:
                        print(content, end="", flush=True)
                        full_response += content
            
            print("\n")  # New line after response
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()

