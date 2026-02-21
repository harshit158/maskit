import base64

import streamlit as st
import pymupdf
import time
from src.maskit.maskit import Masker, PIIEntity
from src.settings import settings
from src.types import LLMProvider
from pydantic import BaseModel, Field
import traceback
from io import BytesIO

class SessionState(BaseModel):
    """Session state class"""
    llm_provider: LLMProvider | None = Field(default=LLMProvider.OLLAMA, description="LLM provider selected by user")
    api_key: str | None = Field(default=None, description="API key for LLM provider")
    from_page_no: int | None = Field(default=None, description="From page number for processing")
    to_page_no: int | None = Field(default=None, description="To page number for processing")
    input_pdf: bytes | None = Field(default=None, description="Uploaded PDF file bytes")
    highlighted_pdf: bytes | None = Field(default=None, description="PDF bytes with highlighted PIIs")
    masked_pdf: bytes | None = Field(default=None, description="PDF bytes with redacted PIIs")
    entities: list[PIIEntity] | None = Field(default=None, description="List of PII entities extracted from the document")

class MaskItApp:
    def __init__(self):
        if "session_state" not in st.session_state:
            st.session_state.session_state = SessionState()
        self.masker = Masker(self.state.llm_provider)
    
    @property
    def state(self):
        return st.session_state.session_state
    
    def _display_steps(self):
        st.markdown("**Steps:** ")
        st.markdown("1. Configure redaction options below")
        st.markdown("2. Upload a PDF document containing PII data")
        st.markdown("3. Click **Extract PIIs**")
        st.markdown("4. Review extracted PIIs in the right panel")
        st.markdown("5. Click **Mask PII** to download the redacted version")
        
    def render_sidebar(self):
        """Render sidebar configuration section"""
        with st.sidebar:
            self._display_steps()
            st.divider()
            
            st.header("Configuration")
            
            self.state.llm_provider = st.selectbox("Select LLM provider", [LLMProvider.OPENAI, LLMProvider.OLLAMA], index=1)
            
            if self.state.llm_provider == LLMProvider.OPENAI:
                self.state.api_key = st.text_input("Enter OpenAI API key", type="password")
                if self.state.api_key:
                    settings.openai_api_key = self.state.api_key
                    st.success("✓ API key set")
                else:
                    st.warning("⚠ Enter your OpenAI API key to proceed")
            
            st.divider()
            st.subheader("Redaction Options")
            
            self.state.from_page_no = st.text_input("From page number", value="1")
            self.state.to_page_no = st.text_input("To page number", value="")
            
            st.divider()
            if st.button("Extract PII", use_container_width=True):
                print("Extracting PIIs...")
                self.state.entities = self.extract_pii()
    
    def _render_pdf(self, pdf: BytesIO | None):
        base64_pdf = base64.b64encode(pdf.getvalue()).decode('utf-8')

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#zoom=125" width="100%" height="2000" type="application/pdf"></iframe>'
        st.markdown(f'<div class="fullwidth"> {pdf_display} </div>', unsafe_allow_html=True)
    
    def render_main_section(self):
        """Render main upload and process section"""
        
        self.state.input_pdf = st.file_uploader("Upload PDF file", type=["pdf"])
            
        if self.state.input_pdf:
            tab1, tab2, tab3 = st.tabs(["Preview", "PII Highlight", "Redacted PDF"])
            with tab1:
                st.subheader("PDF Preview")
                self._render_pdf(self.state.input_pdf)
            
            with tab2:
                st.subheader("PII Highlight")
                self.state.highlighted_pdf = self.highlight_pii(self.state.entities)
                self._render_pdf(self.state.highlighted_pdf)
            
            with tab3:
                st.subheader("Redacted PDF")
                self.state.masked_pdf = self.redact_pii(self.state.entities)
                self._render_pdf(self.state.masked_pdf)
            
        else:
            st.info("📤 Upload a PDF file to begin")
    
    def extract_pii(self) -> list[PIIEntity] | None:
        """Extract PII from uploaded PDF and highlight them"""
        with st.spinner("Extracting PIIs..."):
            try:
                self.state.input_pdf.seek(0)
                doc = pymupdf.open(stream=self.state.input_pdf.read(), filetype="pdf")
                entities = self.masker.extract_pii(doc,
                                                   from_page_no=self.state.from_page_no, 
                                                   to_page_no=self.state.to_page_no)

                return entities
            except Exception as e:
                st.error(f"❌ Error extracting PIIs: {str(e)}")
                st.code(traceback.format_exc(), language="python")
                return None
    
    def highlight_pii(self, entities: list[PIIEntity]) -> BytesIO | None:
        """Highlight extracted PIIs in the PDF preview"""
        try:
            self.state.input_pdf.seek(0)
            doc = pymupdf.open(stream=self.state.input_pdf.read(), filetype="pdf")
            highlighted_pdf = self.masker.highlight_pii(doc, entities)
            return BytesIO(highlighted_pdf)
        except Exception as e:
            st.error(f"❌ Error highlighting PIIs: {str(e)}")
            st.code(traceback.format_exc(), language="python")
    
    def redact_pii(self, entities: list[PIIEntity]) -> BytesIO | None:
        """Redact extracted PIIs and return redacted PDF bytes"""
        try:
            self.state.input_pdf.seek(0)
            doc = pymupdf.open(stream=self.state.input_pdf.read(), filetype="pdf")
            redacted_pdf = self.masker.redact_pii(doc, entities)
            return BytesIO(redacted_pdf)
        except Exception as e:
            st.error(f"❌ Error redacting PIIs: {str(e)}")
            st.code(traceback.format_exc(), language="python")
    
    def render_pii_section(self):
        """Render extracted PIIs section"""
        st.subheader("Extracted PIIs")
        st.divider()
        
        # display entities is present
        if self.state.entities:
            for entity in self.state.entities:
                st.write(f"**{entity.type}**: {entity.text}")
        else:
            st.info("No PIIs extracted yet.")
    
    def _display_pii_entities(self, entities):
        """Display PIIs grouped by entity type"""
        entity_dict = {}
        for entity in entities:
            entity_type = entity.type
            if entity_type not in entity_dict:
                entity_dict[entity_type] = []
            entity_dict[entity_type].append(entity.text)
        
        for entity_type, texts in entity_dict.items():
            with st.expander(f"**{entity_type.upper()}** ({len(texts)})"):
                for text in texts:
                    st.caption(f"• {text}")
    
    def run(self):
        """Main app execution"""
        st.set_page_config(layout="wide", page_title="MaskIt")
        st.title("MaskIt - PII Redaction Tool")
        
        self.render_sidebar()
        
        col_main, col_pii = st.columns([3, 1], gap="large")
        
        with col_main:
            self.render_main_section()
        
        with col_pii:
            self.render_pii_section()


if __name__ == "__main__":
    app = MaskItApp()
    app.run()