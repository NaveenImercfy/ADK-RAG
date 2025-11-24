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

from google.auth import default
from google.api_core.exceptions import ResourceExhausted
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import requests
import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
CORPUS_DISPLAY_NAME = "Student_Textbooks_Corpus"
CORPUS_DESCRIPTION = "Corpus containing student textbooks organized by education board, grade, and subject"

# --- Textbook Configuration ---
# Define your textbooks as a list of dictionaries with board, grade, subject, and PDF information
# Each textbook should have: board, grade, subject, pdf_url (optional), pdf_path (optional), display_name
# Example structure:
TEXTBOOKS = [
    {
        "board": "CBSE",
        "grade": "Grade 10",
        "subject": "Science",
        "pdf_url": "https://firebasestorage.googleapis.com/v0/b/aitrack-29a9e.appspot.com/o/4_Science_Term_1.pdf?alt=media&token=a5c75861-5524-475e-925a-c070d757dace",
        "display_name": "CBSE_Grade10_Science_Term1.pdf",
        "description": "CBSE Grade 10 Science Textbook - Term 1"
    },
    # Add more textbooks here following the same structure:
    # {
    #     "board": "CBSE",
    #     "grade": "Grade 10",
    #     "subject": "Mathematics",
    #     "pdf_url": "https://example.com/cbse-grade10-math.pdf",
    #     "display_name": "CBSE_Grade10_Mathematics.pdf",
    #     "description": "CBSE Grade 10 Mathematics Textbook"
    # },
    # {
    #     "board": "ICSE",
    #     "grade": "Class 9",
    #     "subject": "English",
    #     "pdf_path": "/path/to/local/file.pdf",  # Use pdf_path for local files
    #     "display_name": "ICSE_Class9_English.pdf",
    #     "description": "ICSE Class 9 English Textbook"
    # },
]

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# --- Start of the script ---
def initialize_vertex_ai():
  credentials, _ = default()
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """Creates a new corpus or retrieves an existing one."""
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
  return corpus


def download_pdf_from_url(url, output_path):
  """Downloads a PDF file from the specified URL."""
  print(f"Downloading PDF from {url}...")
  response = requests.get(url, stream=True)
  response.raise_for_status()  # Raise an exception for HTTP errors
  
  with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
      f.write(chunk)
  
  print(f"PDF downloaded successfully to {output_path}")
  return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
  """Uploads a PDF file to the specified corpus."""
  print(f"Uploading {display_name} to corpus...")
  try:
    rag_file = rag.upload_file(
        corpus_name=corpus_name,
        path=pdf_path,
        display_name=display_name,
        description=description,
    )
    print(f"Successfully uploaded {display_name} to corpus")
    return rag_file
  except ResourceExhausted as e:
    print(f"Error uploading file {display_name}: {e}")
    print("\nThis error suggests that you have exceeded the API quota for the embedding model.")
    print("This is common for new Google Cloud projects.")
    print("Please see the 'Troubleshooting' section in the README.md for instructions on how to request a quota increase.")
    return None
  except Exception as e:
    print(f"Error uploading file {display_name}: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
  """Lists files in the specified corpus."""
  files = list(rag.list_files(corpus_name=corpus_name))
  print(f"Total files in corpus: {len(files)}")
  for file in files:
    print(f"File: {file.display_name} - {file.name}")


def process_textbook(corpus_name, textbook, temp_dir=None):
    """Process a single textbook: download if needed and upload to corpus."""
    board = textbook.get("board", "Unknown")
    grade = textbook.get("grade", "Unknown")
    subject = textbook.get("subject", "Unknown")
    display_name = textbook.get("display_name", f"{board}_{grade}_{subject}.pdf")
    description = textbook.get("description", f"{board} {grade} {subject} Textbook")
    pdf_url = textbook.get("pdf_url")
    pdf_path = textbook.get("pdf_path")
    
    # Determine the source PDF path
    if pdf_path:
        # Use local file
        if not os.path.exists(pdf_path):
            print(f"Warning: Local file not found at {pdf_path}. Skipping {display_name}.")
            return None
        source_pdf_path = pdf_path
    elif pdf_url:
        # Download from URL
        if temp_dir is None:
            raise ValueError("temp_dir must be provided when downloading from URL")
        downloaded_path = os.path.join(temp_dir, display_name)
        try:
            download_pdf_from_url(pdf_url, downloaded_path)
            source_pdf_path = downloaded_path
        except Exception as e:
            print(f"Error downloading {display_name} from URL: {e}. Skipping.")
            return None
    else:
        print(f"Warning: No pdf_url or pdf_path provided for {display_name}. Skipping.")
        return None
    
    # Upload to corpus
    return upload_pdf_to_corpus(
        corpus_name=corpus_name,
        pdf_path=source_pdf_path,
        display_name=display_name,
        description=description
    )


def main():
  initialize_vertex_ai()
  corpus = create_or_get_corpus()

  # Update the .env file with the corpus name
  update_env_file(corpus.name, ENV_FILE_PATH)
  
  if not TEXTBOOKS:
      print("Warning: No textbooks configured. Please add textbooks to the TEXTBOOKS list in the script.")
      print("Listing existing files in corpus...")
      list_corpus_files(corpus_name=corpus.name)
      return
  
  # Process all textbooks
  print(f"\nProcessing {len(TEXTBOOKS)} textbook(s)...")
  
  # Create a temporary directory for downloaded PDFs
  with tempfile.TemporaryDirectory() as temp_dir:
      uploaded_count = 0
      for i, textbook in enumerate(TEXTBOOKS, 1):
          print(f"\n[{i}/{len(TEXTBOOKS)}] Processing: {textbook.get('display_name', 'Unknown')}")
          result = process_textbook(corpus.name, textbook, temp_dir)
          if result:
              uploaded_count += 1
  
  print(f"\n{'='*60}")
  print(f"Upload complete: {uploaded_count}/{len(TEXTBOOKS)} textbook(s) uploaded successfully")
  print(f"{'='*60}")
  
  # List all files in the corpus
  print("\nFiles in corpus:")
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main()
