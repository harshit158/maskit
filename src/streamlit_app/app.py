import streamlit as st
import os
from src.maskit.maskit import Masker, LLMProvider
from src.settings import settings


def run_app():
    st.title("MaskIt")
    st.write("Redact text in a PDF file")

    llm_provider = st.selectbox("Select LLM provider", ["openai", "ollama"])
    if llm_provider == "openai":
        api_key = st.text_input("Enter OpenAI API key", type="password")
        if api_key:
            settings.openai_api_key = api_key
            st.success("API key set successfully")
        else:
            st.warning("Please enter your OpenAI API key to proceed")
        
    input_pdf = st.file_uploader("Upload PDF file", type=["pdf"])
    from_page_no = st.text_input("From page number to start redaction")
    to_page_no = st.text_input("To page number to end redaction")


    if st.button("Redact PDF", use_container_width=True):
        masker = Masker(LLMProvider(llm_provider))
        output_doc = masker.mask(input_pdf=input_pdf, from_page_no=from_page_no, to_page_no=to_page_no)
        st.download_button(label="Download Redacted PDF", data=output_doc, file_name="redacted.pdf", use_container_width=True)


if __name__ == "__main__":
    run_app()