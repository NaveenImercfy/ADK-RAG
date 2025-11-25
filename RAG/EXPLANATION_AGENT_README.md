# Sequential Explanation Agent

## Overview

The Sequential Explanation Agent is a workflow agent that provides explanations for student questions based on their education board, grade level, and subject. It uses a three-stage sequential workflow to extract context, retrieve relevant textbook content, and generate age-appropriate explanations.

This agent is specifically designed to work with the RAG corpus containing student textbooks. The RAG agent is used **only** for retrieving information from textbooks in the corpus, ensuring curriculum-aligned responses.

## Architecture

The Sequential Explanation Agent follows the [ADK Sequential Agent pattern](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) and consists of three sub-agents that execute in a fixed order:

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. Context Extractor Agent          │
│    - Extracts board, grade, subject  │
│    - Output: student_context         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. RAG Retrieval Agent              │
│    - Retrieves from textbook corpus │
│    - Uses context for targeted query│
│    - Output: retrieved_content      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Explanation Generator Agent       │
│    - Generates grade-appropriate exp. │
│    - Includes citations              │
│    - Output: final_explanation       │
└─────────────────────────────────────┘
    ↓
Final Response to User
```

## Agent Components

### 1. Context Extractor Agent

**File:** `rag/agents/context_extractor_agent.py`  
**Prompts:** `rag/prompts/context_extractor_prompts.py`

**Purpose:** Analyzes user queries to extract:
- Education Board (e.g., CBSE, ICSE, State Board, IB, etc.)
- Grade Level (e.g., Grade 10, Class 9, etc.)
- Subject (e.g., Mathematics, Science, English, etc.)

**Output Key:** `student_context`

**Example:**
- Input: "I'm studying CBSE Grade 10 Science. Can you explain photosynthesis?"
- Output: `{"board": "CBSE", "grade": "Grade 10", "subject": "Science"}`

### 2. RAG Retrieval Agent

**File:** `rag/agents/rag_retrieval_agent.py`  
**Prompts:** `rag/prompts/rag_retrieval_prompts.py`

**Purpose:** Retrieves relevant content from student textbooks in the RAG corpus based on the extracted context.

**Key Features:**
- Uses Vertex AI RAG Retrieval tool
- Constructs targeted queries: `"[board] [grade] [subject]: [question]"`
- Filters results to match student's board, grade, and subject
- Retrieves top 5 most relevant chunks

**Output Key:** `retrieved_content`

**Example Query Format:**
- "CBSE Grade 10 Science: What is photosynthesis?"

### 3. Explanation Generator Agent

**File:** `rag/agents/explanation_generator_agent.py`  
**Prompts:** `rag/prompts/explanation_generator_prompts.py`

**Purpose:** Synthesizes retrieved content into clear, age-appropriate explanations tailored to the student's grade level.

**Key Features:**
- Grade-appropriate language and complexity
- Curriculum-aligned explanations
- Proper citations
- Engaging and educational tone

**Output Key:** `final_explanation`

**Grade Level Adaptations:**
- **Lower Grades (1-5):** Simple language, visual descriptions, relatable examples
- **Middle Grades (6-8):** Technical terms with explanations, structured examples
- **Higher Grades (9-12):** Advanced terminology, deeper analysis, connections

## File Structure

```
rag/
├── explanation_agent.py          # Main sequential agent
├── agents/
│   ├── __init__.py
│   ├── context_extractor_agent.py
│   ├── rag_retrieval_agent.py
│   └── explanation_generator_agent.py
└── prompts/
    ├── __init__.py
    ├── context_extractor_prompts.py
    ├── rag_retrieval_prompts.py
    └── explanation_generator_prompts.py
```

## Usage

### Basic Usage

```python
from rag.explanation_agent import explanation_agent

# The agent is ready to use
# It will process queries through the three-stage workflow
```

### Custom Configuration

```python
from rag.explanation_agent import create_explanation_agent

# Create a custom agent with different model
agent = create_explanation_agent(
    model='gemini-2.0-flash',
    name='custom_explanation_agent'
)
```

### Running the Agent

#### Using ADK CLI

```bash
# Run the explanation agent
adk run explanation_agent
```

#### Using ADK Web UI

```bash
adk web
# Select "explanation_agent" from the dropdown
```

#### Using Python Runner Script

```bash
# Run the interactive Python script
uv run python run_explanation_agent.py
```

#### Programmatic Usage

```python
from rag.explanation_agent import explanation_agent
from google.adk.runner import InMemoryRunner

runner = InMemoryRunner(explanation_agent, "explanation_agent")
session = runner.session_service().create_session("explanation_agent", "user_123")

# Run a query
response = runner.run_async(
    "user_123",
    session.id(),
    "I'm studying CBSE Grade 10 Science. Can you explain photosynthesis?"
)
```

## Example Interactions

### Example 1: Complete Context Provided

**User Query:**
```
I'm studying CBSE Grade 10 Science. Can you explain what photosynthesis is?
```

**Agent Process:**
1. **Context Extractor:** Extracts `{"board": "CBSE", "grade": "Grade 10", "subject": "Science"}`
2. **RAG Retrieval:** Queries corpus with "CBSE Grade 10 Science: What is photosynthesis?"
3. **Explanation Generator:** Creates grade-appropriate explanation with citations

**Expected Response:**
```
Photosynthesis is the process by which green plants make their own food using 
sunlight, water, and carbon dioxide. During this process, plants absorb sunlight 
through their leaves, take in water from their roots, and carbon dioxide from the 
air. They convert these into glucose (a type of sugar) and release oxygen as a 
byproduct. This process is essential for life on Earth as it produces oxygen that 
we breathe and provides food for plants.

Citations:
1) CBSE Grade 10 Science Textbook - Chapter 6: Life Processes
```

### Example 2: Partial Context

**User Query:**
```
Explain Newton's laws for Grade 11 Physics
```

**Agent Process:**
1. **Context Extractor:** Extracts `{"board": "Not Specified", "grade": "Grade 11", "subject": "Physics"}`
2. **RAG Retrieval:** Attempts retrieval (may be less targeted without board)
3. **Explanation Generator:** Generates explanation appropriate for Grade 11

### Example 3: No Context

**User Query:**
```
What is a quadratic equation?
```

**Agent Process:**
1. **Context Extractor:** Extracts `{"board": "Not Specified", "grade": "Not Specified", "subject": "Not Specified"}`
2. **RAG Retrieval:** Retrieves general content (may need to ask for context)
3. **Explanation Generator:** Provides general explanation or requests more context

## State Management

The SequentialAgent uses shared state to pass data between sub-agents:

- **`student_context`**: Extracted board, grade, and subject (from Context Extractor)
- **`retrieved_content`**: Retrieved textbook chunks (from RAG Retrieval)
- **`final_explanation`**: Final explanation with citations (from Explanation Generator)

All sub-agents share the same `InvocationContext`, allowing them to access previous outputs through state.

## Configuration

### Environment Variables

The agent requires the following environment variables:

```bash
# Required for RAG Retrieval Agent
RAG_CORPUS=projects/<project-number>/locations/<location>/ragCorpora/<corpus-id>

# Optional (defaults set in __init__.py)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Model Configuration

By default, all sub-agents use `gemini-2.5-flash`. You can customize this:

```python
from rag.explanation_agent import create_explanation_agent

agent = create_explanation_agent(model='gemini-2.0-flash')
```

## Key Design Principles

### 1. Separation of Concerns

Each agent has a single, well-defined responsibility:
- **Context Extractor:** Only extracts context
- **RAG Retrieval:** Only retrieves content
- **Explanation Generator:** Only generates explanations

### 2. Modularity

Each agent and prompt is in a separate file, making it easy to:
- Modify individual components
- Test agents independently
- Reuse agents in other workflows

### 3. State-Based Communication

Agents communicate through shared state using output keys:
- No direct agent-to-agent communication
- Clean separation of data flow
- Easy to debug and trace

### 4. Curriculum Alignment

The agent is specifically designed for curriculum-aligned responses:
- Only uses RAG corpus (textbooks)
- Filters by board, grade, and subject
- Provides curriculum-specific citations

## Differences from Root RAG Agent

| Feature | Root RAG Agent | Sequential Explanation Agent |
|---------|---------------|------------------------------|
| **Architecture** | Single agent | Sequential workflow (3 agents) |
| **Context Extraction** | Handled in prompts | Dedicated agent |
| **Retrieval** | Part of main agent | Dedicated agent |
| **Explanation** | Part of main agent | Dedicated agent |
| **Modularity** | Monolithic | Highly modular |
| **Customization** | Modify prompts | Modify individual agents |
| **Use Case** | General RAG queries | Curriculum-aligned explanations |

## Customization

### Modifying Prompts

Each agent's prompts can be customized by editing the corresponding prompt file:

- `rag/prompts/context_extractor_prompts.py`
- `rag/prompts/rag_retrieval_prompts.py`
- `rag/prompts/explanation_generator_prompts.py`

### Adding New Agents

To add a new stage to the workflow:

1. Create agent file in `rag/agents/`
2. Create prompt file in `rag/prompts/`
3. Add agent to `rag/explanation_agent.py` sub_agents list

### Customizing Retrieval

Modify `rag/agents/rag_retrieval_agent.py` to:
- Change `similarity_top_k`
- Adjust `vector_distance_threshold`
- Add additional filtering logic

## Testing

### Unit Testing Individual Agents

```python
from rag.agents import create_context_extractor_agent

agent = create_context_extractor_agent()
# Test the agent independently
```

### Integration Testing

Test the full sequential workflow:

```python
from rag.explanation_agent import explanation_agent
from google.adk.runner import InMemoryRunner

runner = InMemoryRunner(explanation_agent, "explanation_agent")
# Test full workflow
```

## Troubleshooting

### RAG_CORPUS Not Set

**Error:** `ValueError: RAG_CORPUS environment variable is not set`

**Solution:** Set `RAG_CORPUS` in your `.env` file:
```bash
RAG_CORPUS=projects/<project-number>/locations/<location>/ragCorpora/<corpus-id>
```

### No Context Extracted

**Issue:** Agent extracts "Not Specified" for all fields

**Solution:** Ensure user queries include board, grade, and subject information, or modify the context extractor prompt to better infer context.

### Poor Retrieval Results

**Issue:** Retrieved content doesn't match student's context

**Solution:**
- Verify textbook PDFs are properly named with board, grade, and subject
- Check that RAG corpus contains textbooks for the specified board/grade/subject
- Adjust `similarity_top_k` or `vector_distance_threshold` in `rag_retrieval_agent.py`

### Explanation Not Grade-Appropriate

**Issue:** Explanations are too complex or too simple

**Solution:** Modify `rag/prompts/explanation_generator_prompts.py` to adjust grade-level adaptations.

## Best Practices

1. **Always provide context:** Encourage users to specify board, grade, and subject
2. **Verify corpus content:** Ensure corpus contains textbooks for all supported boards/grades/subjects
3. **Monitor retrieval quality:** Check that retrieved chunks match student context
4. **Test grade adaptations:** Verify explanations are appropriate for each grade level
5. **Maintain citations:** Ensure all explanations include proper citations

## References

- [ADK Sequential Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
- [Google ADK Documentation](https://google.github.io/adk-docs/)

## License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

