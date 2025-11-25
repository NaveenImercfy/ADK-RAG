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

"""Prompt modules for agent instructions.

This package contains prompt modules that define instruction prompts for
each agent in the sequential explanation workflow.
"""

import sys
from pathlib import Path

# Import from the old prompts.py file for backward compatibility
# This is needed because rag/agent.py imports from .prompts
_parent_dir = Path(__file__).parent.parent
_prompts_file = _parent_dir / "prompts.py"

if _prompts_file.exists():
    # Import the function from the old prompts.py file
    import importlib.util
    spec = importlib.util.spec_from_file_location("rag.prompts_legacy", _prompts_file)
    prompts_legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompts_legacy)
    return_instructions_root = prompts_legacy.return_instructions_root
else:
    # Fallback if prompts.py doesn't exist
    def return_instructions_root():
        return "Default instructions"

from .context_extractor_prompts import return_instructions_context_extractor
from .explanation_generator_prompts import return_instructions_explanation_generator
from .rag_retrieval_prompts import return_instructions_rag_retrieval

__all__ = [
    'return_instructions_root',  # For backward compatibility with rag/agent.py
    'return_instructions_context_extractor',
    'return_instructions_rag_retrieval',
    'return_instructions_explanation_generator',
]

