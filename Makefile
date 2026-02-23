.PHONY: help frontend install clean

help:
	@echo "Available commands:"
	@echo "  make frontend   - Run the Streamlit app"
	@echo "  make install    - Install dependencies"

frontend:
	streamlit run src/streamlit_app/app.py

setup:
	uv sync