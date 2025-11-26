# How Context Extractor Agent Connects with RAG Retrieval Agent

## Architecture Overview

The Explanation Agent uses a **Sequential Agent** pattern with three sub-agents that execute in order:

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. Context Extractor Agent          │
│    - Extracts: board, grade, subject│
│    - Output Key: 'student_context'  │
│    - Stores in: state['student_context'] │
└─────────────────────────────────────┘
    ↓ (state['student_context'] passed automatically)
┌─────────────────────────────────────┐
│ 2. RAG Retrieval Agent              │
│    - Reads: state['student_context']│
│    - Uses tool: retrieve_student_textbook_content │
│    - Output Key: 'retrieved_content'│
│    - Stores in: state['retrieved_content'] │
└─────────────────────────────────────┘
    ↓ (state['retrieved_content'] passed automatically)
┌─────────────────────────────────────┐
│ 3. Explanation Generator Agent      │
│    - Reads: state['retrieved_content']│
│    - Generates explanation          │
│    - Output Key: 'final_explanation'│
└─────────────────────────────────────┘
```

## Connection Mechanism

### 1. Context Extractor → RAG Retrieval

**How it works:**
- Context Extractor Agent has `output_key='student_context'`
- When it completes, it stores its output in `state['student_context']`
- RAG Retrieval Agent runs next and can access `state['student_context']`
- Both agents share the same `InvocationContext` in SequentialAgent

**Code:**
```python
# Context Extractor Agent
agent = Agent(
    name='ContextExtractorAgent',
    output_key='student_context',  # Stores here
    ...
)

# RAG Retrieval Agent  
agent = Agent(
    name='RagRetrievalAgent',
    # Can access state['student_context'] from previous agent
    ...
)
```

### 2. How RAG Agent Accesses Context

The RAG agent needs to:
1. Read `state['student_context']` which contains JSON like:
   ```json
   {"board": "Tamil Nadu State Board", "grade": "Grade 4", "subject": "English"}
   ```
2. Extract board, grade, subject from the JSON
3. Get the original user question from conversation
4. Construct query: "[board] [grade] [subject]: [question]"
5. Use the retrieval tool with this query

## Comparison: Old vs New Agent

### Old Agent (agent.py) - Works Fine ✅
```python
root_agent = Agent(
    model='gemini-2.5-flash',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[ask_vertex_retrieval],  # Tool directly attached
)
```

**Why it works:**
- Single agent with tool directly attached
- Agent can directly use the tool
- Tool description says "Use this tool" - model understands it
- No state passing needed - everything in one agent

### New Agent (explanation_agent.py) - Has Issues ❌
```python
sequential_agent = SequentialAgent(
    sub_agents=[
        context_extractor,  # Extracts context
        rag_retrieval,      # Needs to read context + use tool
        explanation_generator,
    ],
)
```

**Why it might not work:**
- RAG agent is a separate agent in a sequence
- Needs to read state from previous agent
- Tool might not be invoked correctly
- Instructions might be confusing the model

## Key Differences

| Aspect | Old Agent | New Agent |
|--------|-----------|-----------|
| **Architecture** | Single agent | Sequential (3 agents) |
| **Tool Access** | Direct | Through sub-agent |
| **Context** | Extracted in prompts | Extracted by separate agent |
| **State** | No state passing | Uses state['student_context'] |
| **Tool Description** | "Use this tool" | Changed to "Searches..." |

## The Problem

The RAG agent is trying to write code:
```
print(default_api.retrieve_student_textbook_content(...))
```

Instead of using function calling. This suggests:
1. The model doesn't understand it should use the tool automatically
2. The tool description might be confusing
3. The instructions might be making it think it needs to write code

## Solution Applied

1. **Updated tool description** to match the working agent.py pattern
2. **Clarified instructions** on how to access state['student_context']
3. **Removed confusing language** about "using tools" that might trigger code writing

## How to Verify Connection

The connection works through:
1. **SequentialAgent** ensures agents run in order
2. **Shared InvocationContext** allows state sharing
3. **output_key** mechanism stores/retrieves data:
   - Context Extractor: `output_key='student_context'` → `state['student_context']`
   - RAG Retrieval: Reads `state['student_context']`, writes `state['retrieved_content']`
   - Explanation Generator: Reads `state['retrieved_content']`

## Debugging Steps

If RAG agent still doesn't work:

1. **Check if context is being extracted:**
   - Verify Context Extractor outputs valid JSON
   - Check that state['student_context'] contains the expected data

2. **Check if RAG agent reads context:**
   - Verify RAG agent can access state['student_context']
   - Check if it's parsing the JSON correctly

3. **Check tool invocation:**
   - Verify tool is attached to RAG agent
   - Check if model is using function calling or writing code
   - Compare tool description with working agent.py

4. **Check query construction:**
   - Verify query format: "[board] [grade] [subject]: [question]"
   - Check if board/grade/subject are correctly extracted

