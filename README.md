# MaskIt

PII detection and redaction tool for PDF documents using LLMs.

## Features

- LLM-powered PII extraction (OpenAI GPT or Ollama)
- Detects names, emails, phone numbers, addresses, account numbers
- Web interface built with Streamlit
- Three-view workflow: preview, highlight, redact

## Setup

Prerequisites:
- Python 3.11+
- Ollama or OpenAI API key
- `uv` for dependency management

```bash
git clone https://github.com/harshit158/maskit.git
cd maskit
make install
```

## Running

```bash
make frontend
```

Opens Streamlit app at `http://localhost:8501`

## Usage

1. Choose LLM provider (OpenAI or Ollama) and enter API key if needed
2. Set page range (optional)
3. Upload PDF
4. Click "Extract PII"
5. Review results in three tabs: Preview, Highlight, Redact

## Configuration

Set environment variables in `.env`:

```env
OPENAI_API_KEY=your-api-key
OLLAMA_MODEL_ID=llama2
```

Supports: OpenAI (GPT-4, GPT-3.5), Ollama (Llama2, Mistral, etc.)

## Commands

```bash
make frontend  # Run Streamlit app
make install   # Install dependencies
make help      # Show all commands
```

## Tech Stack

- Streamlit (frontend)
- Python 3.11+
- PyMuPDF for PDF processing
- LangChain for LLM integration
- Pydantic for data validation