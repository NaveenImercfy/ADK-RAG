# Sequential Explanation Agent - Quick Start Guide

## Overview

The Sequential Explanation Agent provides explanations for student questions based on their board, grade, and subject. It uses a three-stage workflow:

1. **Context Extraction** → Extracts board, grade, subject
2. **RAG Retrieval** → Retrieves content from textbooks
3. **Explanation Generation** → Creates grade-appropriate explanations

## Quick Start

### 1. Prerequisites

Ensure you have:
- RAG corpus set up with student textbooks
- `RAG_CORPUS` environment variable configured in `.env`

### 2. Import and Use

```python
from rag.explanation_agent import explanation_agent

# The agent is ready to use!
# It will automatically process queries through the three-stage workflow
```

### 3. Run the Agent

#### Option 1: Using ADK CLI (Recommended)

```bash
# Run the explanation agent
adk run explanation_agent
```

#### Option 2: Using ADK Web UI

```bash
adk web
# Select "explanation_agent" from the dropdown
```

#### Option 3: Using Python Runner Script

```bash
# Run the interactive Python script
uv run python run_explanation_agent.py
```

Or directly:

```bash
python run_explanation_agent.py
```

## Example Usage

### Example 1: Complete Context

**Query:**
```
I'm studying CBSE Grade 10 Science. Can you explain what photosynthesis is?
```

**Result:**
- Context Extractor extracts: `{"board": "CBSE", "grade": "Grade 10", "subject": "Science"}`
- RAG Retrieval queries: `"CBSE Grade 10 Science: What is photosynthesis?"`
- Explanation Generator creates grade-appropriate explanation with citations

### Example 2: Partial Context

**Query:**
```
Explain Newton's laws for Grade 11 Physics
```

**Result:**
- Context Extractor extracts: `{"board": "Not Specified", "grade": "Grade 11", "subject": "Physics"}`
- RAG Retrieval attempts retrieval (may be less targeted)
- Explanation Generator creates Grade 11-appropriate explanation

## File Structure

```
rag/
├── explanation_agent.py          # Main sequential agent
├── agents/
│   ├── context_extractor_agent.py
│   ├── rag_retrieval_agent.py
│   └── explanation_generator_agent.py
└── prompts/
    ├── context_extractor_prompts.py
    ├── rag_retrieval_prompts.py
    └── explanation_generator_prompts.py
```

## Customization

### Change Model

```python
from rag.explanation_agent import create_explanation_agent

agent = create_explanation_agent(model='gemini-2.0-flash')
```

### Modify Prompts

Edit the prompt files in `rag/prompts/`:
- `context_extractor_prompts.py` - Context extraction logic
- `rag_retrieval_prompts.py` - Retrieval instructions
- `explanation_generator_prompts.py` - Explanation generation style

### Modify Agents

Edit the agent files in `rag/agents/`:
- `context_extractor_agent.py` - Context extraction agent
- `rag_retrieval_agent.py` - RAG retrieval agent (adjust retrieval parameters)
- `explanation_generator_agent.py` - Explanation generation agent

## Key Features

✅ **Modular Design** - Each agent in a separate file  
✅ **Separate Prompts** - Each agent has its own prompt file  
✅ **State-Based Communication** - Agents share data through state  
✅ **Curriculum-Aligned** - Only uses RAG corpus (textbooks)  
✅ **Grade-Appropriate** - Tailors explanations to grade level  
✅ **Well-Documented** - Comprehensive documentation and comments  

## Troubleshooting

### RAG_CORPUS Not Set
```bash
# Set in .env file
RAG_CORPUS=projects/<project-number>/locations/<location>/ragCorpora/<corpus-id>
```

### No Context Extracted
- Ensure queries include board, grade, and subject
- Modify `context_extractor_prompts.py` to improve extraction

### Poor Retrieval
- Verify textbook PDFs are properly named
- Check corpus contains textbooks for specified board/grade/subject
- Adjust retrieval parameters in `rag_retrieval_agent.py`

## Documentation

For detailed documentation, see:
- [EXPLANATION_AGENT_README.md](EXPLANATION_AGENT_README.md) - Full documentation
- [ADK Sequential Agents Docs](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) - ADK reference

## Next Steps

1. Test with sample queries
2. Customize prompts for your use case
3. Adjust retrieval parameters if needed
4. Deploy using `deployment/deploy.py`

