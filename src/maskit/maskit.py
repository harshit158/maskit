import pymupdf
from src.llms import get_llm
from src.types import LLMProvider
from argparse import ArgumentParser
from pydantic import BaseModel, Field
from enum import Enum

class EntityType(str, Enum):
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    ACCOUNT_NUMBER = "account_number"
    
class PIIEntity(BaseModel):
    text: str = Field(..., description="The text of the PII entity")
    type: EntityType = Field(..., description="The type of the PII entity (e.g., name, email, etc.)")

class PIIEntities(BaseModel):
    entities: list[PIIEntity] = Field(..., description="List of PII entities extracted from the document")

class Masker:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = get_llm(llm_provider)
    
    def _invoke_llm_for_pii_extraction(self, text: str) -> PIIEntities:
        llm_structured = self.llm.with_structured_output(PIIEntities)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts personally identifiable information (PII) from text. Identify names, emails, phone numbers, addresses, and account numbers."},
            {"role": "user", "content": text}
        ]
        entities = llm_structured.invoke(messages)
        
        return entities
    
    def extract_pii(self, doc, **kwargs) -> list[PIIEntity]:
        pii_entities = []
        from_page = int(kwargs.get("from_page_no", 1)) - 1 if kwargs.get("from_page_no") else 0
        to_page = int(kwargs.get("to_page_no", doc.page_count)) if kwargs.get("to_page_no") else doc.page_count
        
        for page_index in range(from_page, to_page):
            page = doc.load_page(page_index)
            page_text = page.get_text()
            page_pii = self._invoke_llm_for_pii_extraction(page_text)
            pii_entities.extend(page_pii.entities)
        
        return pii_entities

    def highlight_pii(self, doc, entities: list[PIIEntity]) -> bytes:
        if entities:
            for page in doc:
                for entity in entities:
                    text_instances = page.search_for(entity.text)
                    for inst in text_instances:
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_info(content=f"PII Type: {entity.type}")
        return doc.convert_to_pdf()

    def redact_pii(self, doc, entities: list[PIIEntity]) -> bytes:
        if entities:
            for page in doc:
                for entity in entities:
                    text_instances = page.search_for(entity.text)
                    for inst in text_instances:
                        page.add_redact_annot(inst, fill=(0, 0, 0))
                page.apply_redactions()
        return doc.convert_to_pdf()
    
    def mask(self, **kwargs) -> bytes:
        self.kwargs = kwargs
        
        # if pdf is already given:
        if kwargs.get("input_pdf"):
            doc = pymupdf.open(stream=kwargs["input_pdf"].read(), filetype="pdf")
        else:
            doc = pymupdf.open(kwargs["input_path"])
        
        entities_to_redact = self.extract_pii(doc, **kwargs)

        if kwargs.get("highlight_only"):
            # Highlight entities in the document
            doc = self.highlight_pii(doc, entities_to_redact)
        else:
            # Redact entities in the document
            doc = self.redact_pii(doc, entities_to_redact)

        # Return redacted PDF
        return doc

if __name__ == "__main__":
    parser = ArgumentParser(description="Redact text in a PDF file")
    parser.add_argument("--input_path", help="Input PDF file path")
    parser.add_argument("--input_pdf", help="Input PDF")
    parser.add_argument("--output_pdf", required=True, help="Output PDF file path")
    parser.add_argument("--llm_provider", required=True, help="LLM provider to use for PII extraction. Currently supports 'openai' and 'ollama'")
    parser.add_argument("--from_page_no", default=None, help="From page number to start redaction, Defaults to the first page if not provided")
    parser.add_argument("--to_page_no", default=None, help="To page number to end redaction, Defaults to the last page if not provided")
    parser.add_argument("--highlight_only", action="store_true", help="Only highlight PII entities without redaction")

    args = parser.parse_args()
    
    # convert args to dict and pass to masker.mask()
    args = vars(args)

    masker = Masker(LLMProvider(args["llm_provider"]))
    masker.mask(**args)
    
    # Usage example:
    # python src/maskit/maskit.py --input_pdf ../src/data/sample.pdf --output_pdf ../src/data/sample_redacted.pdf --llm_provider openai