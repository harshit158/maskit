import pymupdf
from src.llms import get_llm
from src.types import LLMProvider
from argparse import ArgumentParser
from pydantic import BaseModel, Field

class EntityType(str):
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
    
    def extract_pii(self, doc) -> list[PIIEntity]:
        pii_entities = []
        from_page = int(self.args.from_page_no)-1 if self.args.from_page_no else 0
        to_page = int(self.args.to_page_no) if self.args.to_page_no else doc.page_count
        
        for page_index in range(from_page, to_page):
            page = doc.load_page(page_index)
            page_text = page.get_text()
            page_pii = self._invoke_llm_for_pii_extraction(page_text)
            pii_entities.extend(page_pii.entities)
        
        return pii_entities

    def mask(self, args):
        self.args = args
        
        doc = pymupdf.open(args.input_pdf)
        
        entities_to_redact = self.extract_pii(doc)

        for page in doc:  # iterate pages
            for entity in entities_to_redact:
                # Search for all occurrences of entity text
                text_instances = page.search_for(entity.text)
                for inst in text_instances:
                    # Add redaction annotation
                    page.add_redact_annot(inst, fill=(0, 0, 0))
            
            # Apply redactions for the page
            page.apply_redactions()

        doc.save(args.output_pdf)
        doc.close()

if __name__ == "__main__":
    parser = ArgumentParser(description="Redact text in a PDF file")
    parser.add_argument("--input_pdf", required=True, help="Input PDF file path")
    parser.add_argument("--output_pdf", required=True, help="Output PDF file path")
    parser.add_argument("--llm_provider", required=True, help="LLM provider to use for PII extraction. Currently supports 'openai' and 'ollama'")
    parser.add_argument("--from_page_no", default=None, help="From page number to start redaction, Defaults to the first page if not provided")
    parser.add_argument("--to_page_no", default=None, help="To page number to end redaction, Defaults to the last page if not provided")

    args = parser.parse_args()

    masker = Masker(LLMProvider(args.llm_provider))
    masker.mask(args)
    
    # Usage example:
    # python src/maskit/maskit.py --input_pdf ../src/data/sample.pdf --output_pdf ../src/data/sample_redacted.pdf --llm_provider openai