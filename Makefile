.PHONY: help frontend install clean

help:
	@echo "Available commands:"
	@echo "  make frontend   - Run the Streamlit app"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean up cache"

frontend:
	streamlit run src/streamlit_app/app.py

setup:
	uv sync

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
