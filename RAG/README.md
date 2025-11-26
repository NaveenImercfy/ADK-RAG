# Student Educational RAG Agent

## Overview

This agent is designed to help students learn from their textbooks. It utilizes Retrieval-Augmented Generation (RAG) with the Vertex AI RAG Engine to fetch relevant content from student textbooks organized by education board, grade level, and subject. The agent provides age-appropriate, curriculum-aligned answers based on the student's specific textbook content.


![RAG Architecture](RAG_architecture.png)

This diagram outlines the agent's workflow, designed to provide informed and context-aware responses. When a student asks a question, the agent first identifies their education board, grade level, and subject. The LLM then uses the `VertexAiRagRetrieval` tool with an optimized query that includes the student's context (board, grade, subject) to fetch relevant information primarily from the appropriate textbook. This targeted retrieval approach reduces irrelevant results and improves efficiency. The LLM then filters and synthesizes the retrieved information to generate an age-appropriate, curriculum-aligned answer with citations pointing back to the specific textbook and chapter.

## Agent Details
| Attribute         | Details                                                                                                                                                                                             |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Interaction Type** | Conversational                                                                                                                                                                                      |
| **Complexity**    | Intermediate 
| **Agent Type**    | Single Agent                                                                                                                                                                                        |
| **Components**    | Tools, RAG, Evaluation                                                                                                                                                                               |
| **Vertical**      | Horizontal                                                                                                                                                                               |
### Agent Architecture

![RAG](RAG_workflow.png)


### Key Features

*   **Student-Focused Learning:** Designed specifically for students with age-appropriate explanations
*   **Multi-Board Support:** Works with textbooks from different education boards (CBSE, ICSE, State Boards, IB, etc.)
*   **Grade-Level Appropriate:** Provides answers tailored to the student's grade level
*   **Subject-Specific Retrieval:** Retrieves content from the correct subject textbook
*   **Optimized Retrieval:** Uses context-aware queries (board, grade, subject) in retrieval 
    to make semantic search more targeted, reducing irrelevant results and improving efficiency
*   **Retrieval-Augmented Generation (RAG):** Leverages [Vertex AI RAG
    Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
    to fetch relevant textbook content with optimized queries
*   **Citation Support:** Provides accurate citations for the retrieved content,
    including board, grade, subject, and chapter information.
*   **Clear Instructions:** Adheres to strict guidelines for providing factual,
    curriculum-aligned answers with proper citations.

## Setup and Installation Instructions
### Prerequisites

*   **Google Cloud Account:** You need a Google Cloud account.
*   **Python 3.10+:** Ensure you have Python 3.10 or a later version installed.
*   **uv:** For dependency management and packaging. Please follow the instructions on the official [uv website](https://docs.astral.sh/uv/) for installation.

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

*   **Git:** Ensure you have git installed.

### Project Setup

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/RAG
    ```

2.  **Install Dependencies:**

    ```bash
    uv sync
    ```

    This command reads the `pyproject.toml` file and installs all the necessary dependencies into a virtual environment.

3.  **Set up Environment Variables:**
    Rename the file ".env.example" to ".env" 
    Follow the steps in the file to set up the environment variables.

4. **Setup Corpus:**
    If you have an existing corpus in Vertex AI RAG Engine, please set corpus information in your .env file. For example: RAG_CORPUS='projects/123/locations/us-central1/ragCorpora/456'.

    If you don't have a corpus setup yet, please follow "How to upload textbooks to my RAG corpus" section. The `prepare_corpus_and_data.py` script will automatically create a corpus (if needed) and update the `RAG_CORPUS` variable in your `.env` file with the resource name of the created or retrieved corpus.

#### How to upload textbooks to my RAG corpus

The `rag/shared_libraries/prepare_corpus_and_data.py` script helps you set up a RAG corpus and upload student textbooks organized by education board, grade, and subject. The script supports uploading multiple textbooks from URLs or local files.

1.  **Authenticate with your Google Cloud account:**
    ```bash
    gcloud auth application-default login
    ```

2.  **Set up environment variables in your `.env` file:**
    Ensure your `.env` file (copied from `.env.example`) has the following variables set:
    ```
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=your-location  # e.g., us-central1
    ```

3.  **Configure and run the preparation script:**
    
    Open the `rag/shared_libraries/prepare_corpus_and_data.py` file and configure the `TEXTBOOKS` list with your textbooks. Each textbook should include:
    - `board`: Education board (e.g., "CBSE", "ICSE", "State Board", "IB")
    - `grade`: Grade level (e.g., "Grade 10", "Class 9")
    - `subject`: Subject name (e.g., "Mathematics", "Science", "English")
    - `display_name`: Name for the file in the corpus (should include board, grade, subject)
    - `description`: Description of the textbook
    - Either `pdf_url` (for downloading from URL) or `pdf_path` (for local files)
    
    **Example configuration:**
    ```python
    TEXTBOOKS = [
        {
            "board": "CBSE",
            "grade": "Grade 10",
            "subject": "Science",
            "pdf_url": "https://example.com/cbse-grade10-science.pdf",
            "display_name": "CBSE_Grade10_Science.pdf",
            "description": "CBSE Grade 10 Science Textbook"
        },
        {
            "board": "CBSE",
            "grade": "Grade 10",
            "subject": "Mathematics",
            "pdf_path": "/path/to/local/cbse-grade10-math.pdf",
            "display_name": "CBSE_Grade10_Mathematics.pdf",
            "description": "CBSE Grade 10 Mathematics Textbook"
        },
        {
            "board": "ICSE",
            "grade": "Class 9",
            "subject": "English",
            "pdf_url": "https://example.com/icse-class9-english.pdf",
            "display_name": "ICSE_Class9_English.pdf",
            "description": "ICSE Class 9 English Textbook"
        },
    ]
    ```
    
    **Run the script:**
    ```bash
    uv run python rag/shared_libraries/prepare_corpus_and_data.py
    ```
    
    This will:
    - Create a corpus named `Student_Textbooks_Corpus` (if it doesn't exist)
    - Download or read all textbooks from the `TEXTBOOKS` list
    - Upload each textbook to the corpus with appropriate metadata
    - Update the `RAG_CORPUS` variable in your `.env` file

#### Manual PDF Upload (Recommended for Small Sets)

If you prefer to manually upload PDFs directly to the RAG corpus (e.g., 1-2 PDFs for testing), follow these guidelines:

**PDF Naming Convention:**
- Format: `BOARD_GRADE_SUBJECT.pdf` (or `BOARD_GRADE_SUBJECT1_SUBJECT2_SUBJECT3.pdf` for combined subjects)
- Examples:
  - `CBSE_Grade10_Science.pdf`
  - `ICSE_Class9_Mathematics.pdf`
  - `StateBoard_Grade12_Physics.pdf`
  - `TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf` (combined subjects)

**When Uploading:**
- **Display Name:** Use the same naming convention (e.g., `CBSE_Grade10_Science.pdf`)
- **Description:** Include board, grade, and subject (e.g., `CBSE Grade 10 Science Textbook`)

**Why This Matters:**
The agent uses the display_name and description to filter retrieved content and match it to the student's board, grade, and subject. Proper naming ensures accurate retrieval and citations.

**Example Uploads:**

**Single PDF:**
```
File: CBSE_Grade10_Science.pdf
Display Name: CBSE_Grade10_Science.pdf
Description: CBSE Grade 10 Science Textbook
```

**Multiple Terms (e.g., Tamil Nadu State Board, Grade 4, Science - 3 terms):**
```
Term 1:
File: TamilNaduStateBoard_Grade4_Science_Term1.pdf
Display Name: TamilNaduStateBoard_Grade4_Science_Term1.pdf
Description: Tamil Nadu State Board Grade 4 Science Textbook - Term 1

Term 2:
File: TamilNaduStateBoard_Grade4_Science_Term2.pdf
Display Name: TamilNaduStateBoard_Grade4_Science_Term2.pdf
Description: Tamil Nadu State Board Grade 4 Science Textbook - Term 2

Term 3:
File: TamilNaduStateBoard_Grade4_Science_Term3.pdf
Display Name: TamilNaduStateBoard_Grade4_Science_Term3.pdf
Description: Tamil Nadu State Board Grade 4 Science Textbook - Term 3
```

**Combined Subjects (e.g., Tamil Nadu State Board, Grade 4, Maths/Science/SocialScience - Term 1):**
```
Term 1:
File: TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf
Display Name: TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf
Description: Tamil Nadu State Board Grade 4 Maths, Science, and Social Science Textbook - Term 1
```

**Note:** When a PDF contains multiple subjects, list all subjects separated by underscores. The agent will recognize queries for any of the subjects (e.g., asking about "Science" will match a PDF containing "Maths_Science_SocialScience").

For detailed manual upload instructions, see [MANUAL_UPLOAD_GUIDE.md](MANUAL_UPLOAD_GUIDE.md).

More details about managing data in Vertex RAG Engine can be found in the
[official documentation page](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart).

## Running the Agent
You can run the agent using the ADK command in your terminal.
from the root project directory:

1.  Run agent in CLI:

    ```bash
    adk run rag
    ```

2.  Run agent with ADK Web UI:
    ```bash
    adk web
    ```
    Select the RAG from the dropdown


### Example Interaction
Here's a quick example of how a student might interact with the agent:

**Example 1: Student Question with Context**

Student: I'm studying CBSE Grade 10 Science. Can you explain what photosynthesis is?

Agent: Photosynthesis is the process by which green plants make their own food using sunlight, water, and carbon dioxide. During this process, plants absorb sunlight through their leaves, take in water from their roots, and carbon dioxide from the air. They convert these into glucose (a type of sugar) and release oxygen as a byproduct. This process is essential for life on Earth as it produces oxygen that we breathe and provides food for plants.

Citations:
1) CBSE Grade 10 Science Textbook - Chapter 6: Life Processes

**Example 2: Student Question Without Context**

Student: What is a quadratic equation?

Agent: I'd be happy to help you understand quadratic equations! To provide you with the most accurate answer from your textbook, could you please tell me:
- Your education board (e.g., CBSE, ICSE, Tamil Nadu State Board, Maharashtra State Board, or other state boards)
- Your grade level (e.g., Grade 10, Class 9)
- The subject (e.g., Mathematics)

Once I have this information, I can retrieve the exact explanation from your curriculum textbook.

## Evaluating the Agent

The evaluation can be run from the `RAG` directory using
the `pytest` module:

```bash
uv sync --dev
uv run pytest eval
```

### Evaluation Process

The evaluation framework consists of three key components:

1. **test_eval.py**: The main test script that orchestrates the evaluation process. It uses the `AgentEvaluator` from Google ADK to run the agent against a test dataset and assess its performance based on predefined criteria.

2. **conversation.test.json**: Contains a sequence of test cases structured as a conversation. Each test case includes:
   - A user query (e.g., questions about student curriculum topics)
   - Expected tool usage (which tools the agent should call and with what parameters)
   - Reference answers (ideal responses the agent should provide)

3. **test_config.json**: Defines evaluation criteria and thresholds:
   - `tool_trajectory_avg_score`: Measures how well the agent uses the appropriate tools
   - `response_match_score`: Measures how closely the agent's responses match the reference answers

When you run the evaluation, the system:
1. Loads the test cases from conversation.test.json
2. Sends each query to the agent
3. Compares the agent's tool usage against expected tool usage
4. Compares the agent's responses against reference answers
5. Calculates scores based on the criteria in test_config.json

This evaluation helps ensure the agent correctly identifies student context (board, grade, subject), leverages the RAG capabilities to retrieve relevant textbook content, and generates age-appropriate, curriculum-aligned responses with proper citations.

## Deploying the Agent

The Agent can be deployed to Vertex AI Agent Engine using the following
commands:

```bash
uv run python deployment/deploy.py
```

After deploying the agent, you'll be able to read the following INFO log message:

```
Deployed agent to Vertex AI Agent Engine successfully, resource name: projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
```

Please note your Agent Engine resource name and update `.env` file accordingly as this is crucial for testing the remote agent.

You may also modify the deployment script for your use cases.

## Testing the deployed agent

After deploying the agent, follow these steps to test it:

1. **Update Environment Variables:**
   - Open your `.env` file.
   - The `AGENT_ENGINE_ID` should have been automatically updated by the `deployment/deploy.py` script when you deployed the agent. Verify that it is set correctly:
     ```
     AGENT_ENGINE_ID=projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
     ```

2. **Grant RAG Corpus Access Permissions:**
   - Ensure your `.env` file has the following variables set correctly:
     ```
     GOOGLE_CLOUD_PROJECT=your-project-id
     RAG_CORPUS=projects/<project-number>/locations/us-central1/ragCorpora/<corpus-id>
     ```
   - Run the permissions script:
     ```bash
     chmod +x deployment/grant_permissions.sh
     ./deployment/grant_permissions.sh
     ```
   This script will:
   - Read the environment variables from your `.env` file
   - Create a custom role with RAG Corpus query permissions
   - Grant the necessary permissions to the AI Platform Reasoning Engine Service Agent

3. **Test the Remote Agent:**
   - Run the test script:
     ```bash
     uv run python deployment/run.py
     ```
   This script will:
   - Connect to your deployed agent
   - Send a series of test queries
   - Display the agent's responses with proper formatting

The test script includes example queries. You can modify the queries in `deployment/run.py` to test different aspects of your deployed agent with student questions from various boards, grades, and subjects.

### Testing with Postman

You can also test the deployed agent using Postman for API testing. See [POSTMAN_API_GUIDE.md](POSTMAN_API_GUIDE.md) for:
- Complete Postman collection setup
- API endpoint documentation
- Example requests for different scenarios
- Authentication setup
- Troubleshooting guide

### Integration with Unreal Engine 5

To integrate this agent into Unreal Engine 5 games or educational applications, see [UNREAL_ENGINE_INTEGRATION.md](UNREAL_ENGINE_INTEGRATION.md) for:
- Complete C++ plugin implementation
- Blueprint integration
- UI widget creation
- Session and context management
- Full feature integration including RAG retrieval and citations

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-rag-agent -a adk@rag
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-rag-agent -a adk@rag
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.

## Customization

### Customize Agent
You can customize system instructions for the agent in `rag/prompts.py` to adjust how the agent interacts with students, handles different education boards, or explains concepts. You can also add more tools to suit your needs, for example, google search for additional educational resources.

### Customize Vertex RAG Engine
You can read more about [official Vertex RAG Engine documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart) for more details on customizing corpora and data. For this educational use case, ensure your textbook PDFs are properly named and organized with clear board, grade, and subject information in their display names and descriptions to help the agent retrieve the correct content.

## How the Optimized Retrieval Works

The agent uses an optimized retrieval strategy to improve efficiency and reduce irrelevant results:

### Retrieval Process

1. **Context-Aware Query Construction:**
   - When a student asks a question, the agent includes their board, grade, and subject in the retrieval query
   - Format: `"[board] [grade] [subject]: [student question]"`
   - Example: `"CBSE Grade 10 Science: What is photosynthesis?"`
   - This makes semantic search more targeted toward the correct textbook

2. **Targeted Retrieval:**
   - The Vertex AI RAG Engine performs semantic search across all textbooks
   - By including context in the query, results are biased toward matching textbooks
   - Retrieves top 5 most relevant chunks (reduced from 10 for efficiency)

3. **LLM Filtering:**
   - The LLM receives retrieved chunks with file metadata
   - Filters chunks to use only those from files matching the student's board, grade, and subject
   - Generates answer using filtered, relevant chunks

### Benefits

- **Reduced Retrieval Overhead:** Fewer irrelevant chunks retrieved (5 instead of 10)
- **Better Targeting:** Context in query improves semantic search accuracy
- **Faster Processing:** Less data to filter and process
- **More Accurate Answers:** Focus on relevant textbook content

### Example Flow

```
Student: "I'm studying CBSE Grade 10 Science. What is photosynthesis?"

Agent Process:
1. Identifies context: CBSE, Grade 10, Science
2. Constructs query: "CBSE Grade 10 Science: What is photosynthesis?"
3. Retrieves top 5 chunks (primarily from CBSE Grade 10 Science textbook)
4. Filters to use only CBSE Grade 10 Science chunks
5. Generates answer with citations
```


### Plug-in other retrieval sources
You can also integrate your preferred retrieval sources to enhance the agent's
capabilities. For instance, you can seamlessly replace or augment the existing
`VertexAiRagRetrieval` tool with a tool that utilizes Vertex AI Search or any
other retrieval mechanism. This flexibility allows you to tailor the agent to
your specific data sources and retrieval requirements.


## Troubleshooting

### Quota Exceeded Errors

When running the `prepare_corpus_and_data.py` script, you may encounter an error related to API quotas, such as:

```
Error uploading file ...: 429 Quota exceeded for aiplatform.googleapis.com/online_prediction_requests_per_base_model with base model: textembedding-gecko.
```

This is especially common for new Google Cloud projects that have lower default quotas.

**Solution:**

You will need to request a quota increase for the model you are using.

1.  Navigate to the **Quotas** page in the Google Cloud Console: [https://console.cloud.google.com/iam-admin/quotas](https://console.cloud.google.com/iam-admin/quotas)
2.  Follow the instructions in the official documentation to request a quota increase: [https://cloud.google.com/vertex-ai/docs/quotas#request_a_quota_increase](https://cloud.google.com/vertex-ai/docs/quotas#request_a_quota_increase)


## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.