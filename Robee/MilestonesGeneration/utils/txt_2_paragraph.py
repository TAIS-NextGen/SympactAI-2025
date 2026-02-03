import os
import PyPDF2
from pathlib import Path
import openai 
import re
from dotenv import load_dotenv
load_dotenv()

class PDFCareerTransformer:
    def __init__(self, openai_api_key):

        openai.api_key  = openai_api_key
    
    def extract_text_from_pdf(self, pdf_path):

        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            return text_content
        except Exception as e:
            print(f"Error extracting text from {pdf_file.name}: {str(e)}")
            return None
    
    def transform_career_to_paragraph(self, text_content):

        try:
            prompt = f"""
            Please analyze the following resume/CV text and create a comprehensive career summary paragraph that flows naturally. 
            CRITICAL REQUIREMENTS:
            1. DO NOT drop any information - include ALL work experience, achievements, dates, and details
            2. Preserve all dates EXACTLY as they appear in the original text
            3. Include all job titles, company names, locations, and durations
            4. Mention all achievements, awards, certifications, and rankings
            5. Include all skills, languages, and educational background
            6. Combine everything into a cohesive narrative that flows naturally
            7. Be written in third person
            8. Flow as one continuous, well-structured paragraph
            9. Maintain chronological order where possible
            
            Resume text:
            {text_content}
            
            Please provide only the comprehensive career summary paragraph that includes ALL information, nothing else.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Transform the given career to a full well-structured paragraph without dropping any information. Preserve all dates exactly as they appear."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def process_pdf_to_career_paragraph(self, pdf_path, output_path=None):

        print(f"Extracting text from: {pdf_path}")
        text_content = self.extract_text_from_pdf(pdf_path)
        
        if not text_content:
            print("Failed to extract text from PDF")
            return None
        
        # Transform career information
        print("Transforming career information using OpenAI GPT...")
        career_paragraph = self.transform_career_to_paragraph(text_content)
        
        if not career_paragraph:
            print("Failed to transform career information")
            return None
        
        # Determine output path
        if output_path is None:
            pdf_file = Path(pdf_path)
            output_path = pdf_file.parent / f"{pdf_file.stem}_career_summary.txt"
        
        # Save the transformed content
        try:
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write("=== CAREER SUMMARY ===\n\n")
                output_file.write(career_paragraph)
                output_file.write("\n\n=== ORIGINAL TEXT ===\n\n")
                output_file.write(text_content)
            
            print(f"Career summary saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"Error saving output file: {str(e)}")
            return None
    
    def batch_process_pdfs(self, directory_path):

        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Directory not found: {directory_path}")
            return
        
        # Find all PDF files
        pdf_files = list(directory.rglob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in the directory.")
            return
        
        print(f"Found {len(pdf_files)} PDF file(s) to process...")
        
        successful_processes = 0
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            result = self.process_pdf_to_career_paragraph(str(pdf_file))
            if result:
                successful_processes += 1
        
        print(f"\nProcessing completed: {successful_processes}/{len(pdf_files)} files successfully processed.")

if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    transformer = PDFCareerTransformer(OPENAI_API_KEY)
    
    pdf_path = r".\Firas Baba\Firas Baba.pdf"
    transformer.process_pdf_to_career_paragraph(pdf_path)
    
