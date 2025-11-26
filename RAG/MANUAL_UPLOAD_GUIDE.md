# Manual PDF Upload Guide for RAG Corpus

This guide explains how to manually upload PDFs to the Vertex AI RAG Engine corpus for the Student Educational RAG Agent.

## PDF Naming Convention

For the agent to correctly identify and retrieve content from your PDFs, follow this naming pattern:

### Recommended Format

```
BOARD_GRADE_SUBJECT.pdf
```

### Examples

**Good naming examples:**
- `CBSE_Grade10_Science.pdf`
- `CBSE_Grade10_Mathematics.pdf`
- `ICSE_Class9_English.pdf`
- `ICSE_Class9_History.pdf`
- `StateBoard_Grade12_Physics.pdf`
- `IB_Year11_Chemistry.pdf`

**For multiple terms/parts:**
- `CBSE_Grade10_Science_Term1.pdf`
- `CBSE_Grade10_Science_Term2.pdf`
- `CBSE_Grade10_Mathematics_Part1.pdf`
- `CBSE_Grade10_Mathematics_Part2.pdf`

**Example: Tamil Nadu State Board, Grade 4, Science (3 terms):**
- `TamilNaduStateBoard_Grade4_Science_Term1.pdf`
- `TamilNaduStateBoard_Grade4_Science_Term2.pdf`
- `TamilNaduStateBoard_Grade4_Science_Term3.pdf`

**For combined subjects (multiple subjects in one PDF):**
- `TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf`
- `CBSE_Grade5_Mathematics_Science_English.pdf`
- `ICSE_Class6_Science_Geography_History.pdf`

**Note:** When multiple subjects are combined in one PDF, list all subjects separated by underscores. The agent will recognize and match queries for any of the subjects in the filename.

### Naming Rules

1. **Use underscores (`_`)** to separate components
2. **Board name** should be clear and consistent (e.g., `CBSE`, `ICSE`, `StateBoard`, `IB`)
3. **Grade** can be in format: `Grade10`, `Class9`, `Year11`, etc.
4. **Subject** should be the full subject name (e.g., `Science`, `Mathematics`, `English`)
   - **For combined subjects:** List all subjects separated by underscores (e.g., `Maths_Science_SocialScience`)
5. **Optional:** Add term/part information if needed (e.g., `Term1`, `Part1`)

## Upload Information

When uploading a PDF to the RAG corpus, you need to provide:

### 1. Display Name
- **What it is:** The name shown in the corpus
- **Format:** Should match your PDF filename or follow the naming convention
- **Example:** `CBSE_Grade10_Science.pdf`

### 2. Description
- **What it is:** A description that helps identify the textbook
- **Format:** `[Board] [Grade] [Subject] Textbook`
- **Example:** `CBSE Grade 10 Science Textbook`
- **For multiple terms:** Add term information
  - Example: `Tamil Nadu State Board Grade 4 Science Textbook - Term 1`
  - Example: `Tamil Nadu State Board Grade 4 Science Textbook - Term 2`
  - Example: `Tamil Nadu State Board Grade 4 Science Textbook - Term 3`

## Why This Matters

The agent uses the **display_name** and **description** to:
1. **Filter results** - When a student asks a question, the agent checks if retrieved chunks match their board, grade, and subject
2. **Generate citations** - The display_name appears in citations shown to students
3. **Targeted retrieval** - Context-aware queries work better when file names contain board/grade/subject information

## Manual Upload Steps

### Using Vertex AI Console

1. Go to Vertex AI RAG Engine in Google Cloud Console
2. Select your corpus (or create one)
3. Click "Upload File"
4. Select your PDF file
5. Set **Display Name** following the naming convention
6. Set **Description** with board, grade, and subject
7. Upload

### Using Python SDK

```python
from vertexai.preview import rag

# Your corpus resource name
corpus_name = "projects/YOUR_PROJECT/locations/us-central1/ragCorpora/YOUR_CORPUS_ID"

# Upload with proper naming
rag.upload_file(
    corpus_name=corpus_name,
    path="/path/to/CBSE_Grade10_Science.pdf",
    display_name="CBSE_Grade10_Science.pdf",  # Follow naming convention
    description="CBSE Grade 10 Science Textbook"  # Include board, grade, subject
)
```

### Using gcloud CLI

```bash
gcloud ai rag-files upload \
  --corpus=projects/YOUR_PROJECT/locations/us-central1/ragCorpora/YOUR_CORPUS_ID \
  --source-uri=gs://your-bucket/CBSE_Grade10_Science.pdf \
  --display-name="CBSE_Grade10_Science.pdf" \
  --description="CBSE Grade 10 Science Textbook"
```

## Examples: Uploading PDFs

### Example 1: Single PDF
**CBSE Grade 10 Science:**
- **File:** `CBSE_Grade10_Science.pdf`
- **Display Name:** `CBSE_Grade10_Science.pdf`
- **Description:** `CBSE Grade 10 Science Textbook`

### Example 2: Multiple Terms (Tamil Nadu State Board, Grade 4, Science)
**Term 1:**
- **File:** `TamilNaduStateBoard_Grade4_Science_Term1.pdf`
- **Display Name:** `TamilNaduStateBoard_Grade4_Science_Term1.pdf`
- **Description:** `Tamil Nadu State Board Grade 4 Science Textbook - Term 1`

**Term 2:**
- **File:** `TamilNaduStateBoard_Grade4_Science_Term2.pdf`
- **Display Name:** `TamilNaduStateBoard_Grade4_Science_Term2.pdf`
- **Description:** `Tamil Nadu State Board Grade 4 Science Textbook - Term 2`

**Term 3:**
- **File:** `TamilNaduStateBoard_Grade4_Science_Term3.pdf`
- **Display Name:** `TamilNaduStateBoard_Grade4_Science_Term3.pdf`
- **Description:** `Tamil Nadu State Board Grade 4 Science Textbook - Term 3`

### Example 3: Different Subjects
**ICSE Class 9 Mathematics:**
- **File:** `ICSE_Class9_Mathematics.pdf`
- **Display Name:** `ICSE_Class9_Mathematics.pdf`
- **Description:** `ICSE Class 9 Mathematics Textbook`

### Example 4: Combined Subjects (Multiple Subjects in One PDF)
**Tamil Nadu State Board Grade 4 - Maths, Science, and Social Science (Term 1):**
- **File:** `TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf`
- **Display Name:** `TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf`
- **Description:** `Tamil Nadu State Board Grade 4 Maths, Science, and Social Science Textbook - Term 1`

**Note:** When uploading combined subject PDFs, include all subjects in both the filename and description. The agent will recognize queries for any of the subjects listed (e.g., a query about "Science" will match this PDF).

## Best Practices

1. **Be Consistent:** Use the same naming pattern for all PDFs
2. **Include All Info:** Always include board, grade, and subject in both display_name and description
3. **Use Clear Abbreviations:** If using abbreviations, be consistent (e.g., always use `CBSE` not `cbse` or `C.B.S.E.`)
4. **Avoid Special Characters:** Stick to letters, numbers, and underscores in filenames
5. **Keep It Simple:** Don't add unnecessary information that might confuse the agent

## How the Agent Uses This Information

When a student asks: *"I'm studying Tamil Nadu State Board Grade 4 Science. What is photosynthesis?"*

1. The agent constructs query: `"Tamil Nadu State Board Grade 4 Science: What is photosynthesis?"`
2. Retrieves chunks from the corpus
3. **Filters chunks** by checking if the source file's display_name contains:
   - "TamilNaduStateBoard" (or "Tamil Nadu State Board")
   - "Grade4" (or "Grade 4")
   - "Science" (or "Maths", "SocialScience" if asking about those subjects)
4. Uses chunks from **all matching terms** (Term1, Term2, Term3) if the question doesn't specify a term
5. Citations show: `Tamil Nadu State Board Grade 4 Science Textbook - Term 1` (or appropriate term)

**Note:** When a student doesn't specify a term, the agent will search across all terms (Term1, Term2, Term3) to find the most relevant answer. If you want to restrict to a specific term, the student should mention it in their question.

### Combined Subjects Handling

When a PDF contains multiple subjects (e.g., `TamilNaduStateBoard_Grade4_Maths_Science_SocialScience_Term1.pdf`):

- If a student asks about **Science**, the agent will match this PDF because "Science" is in the filename
- If a student asks about **Maths**, the agent will match this PDF because "Maths" is in the filename
- If a student asks about **SocialScience**, the agent will match this PDF because "SocialScience" is in the filename

The agent checks if the requested subject appears anywhere in the filename, so combined subject PDFs work seamlessly.

## Troubleshooting

**Problem:** Agent retrieves wrong textbook content
- **Solution:** Ensure display_name and description clearly include board, grade, and subject

**Problem:** Citations show incorrect textbook name
- **Solution:** Make sure display_name follows the naming convention

**Problem:** Agent can't find relevant content
- **Solution:** Verify the PDF content matches the board/grade/subject in the filename

