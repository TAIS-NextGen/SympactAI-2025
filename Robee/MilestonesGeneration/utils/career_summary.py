import os
import base64
from pdf2image import convert_from_path
import openai 
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

"""Gets curruclum vitae from a pdf file and transforms it into a career summary 
paragraph using OpenAI Vision API."""

def pdf_to_images(pdf_path):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    try:
        images = convert_from_path(pdf_path , poppler_path=  r'.\Release-24.08.0-0\poppler-24.08.0\Library\bin')
        print(f"Successfully converted PDF to {len(images)} images")
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def analyze_resume_with_openai(images):
    
    prompt = """
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
    
    Please extract and transform all the information from these resume pages into the format specified above.
    """
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]
    
    for idx, image in enumerate(images):
        base64_image = image_to_base64(image)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}",
                "detail": "high"
            }
        })
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4", 
            messages=messages,
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def save_images_temporarily(images):
    image_paths = []
    for idx, image in enumerate(images):
        out_path = f"page_{idx+1}.png"
        image.save(out_path, "PNG")
        image_paths.append(out_path)
        print(f"Saved: {out_path}")
    return image_paths

def cleanup_images(image_paths):
    for path in image_paths:
        try:
            os.remove(path)
            print(f"Cleaned up: {path}")
        except Exception as e:
            print(f"Error removing {path}: {e}")

def main_CS():
    # person = "Firas Baba"


    persons = [d.split('.')[0] for d in os.listdir('./MilestonesGeneration/Persons/names')]
    
    for person in persons:
        # Check if career summary already exists
        career_summary_path = rf".\MilestonesGeneration\{person}\{person}_career_summary.txt"
        if os.path.exists(career_summary_path):
            print(f"Career summary already exists for {person}, skipping...")
            continue
            
        print(f"Processing resume for: {person}")
        pdf_path = rf".\MilestonesGeneration\Persons\linkedin\{person}.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            continue
        
        print("Step 1: Converting PDF to images...")
        images = pdf_to_images(pdf_path)
        
        if not images:
            print("Failed to convert PDF to images")
            return
        
        print("Step 2: Saving images temporarily...")
        image_paths = save_images_temporarily(images)
        
        print("Step 3: Analyzing resume with OpenAI Vision...")
        career_summary = analyze_resume_with_openai(images)
        
        if career_summary:
            print("\n" + "="*80)
            print("CAREER SUMMARY:")
            print("="*80)
            print(career_summary)
            print("="*80)
            
            with open(rf".\MilestonesGeneration\{person}\{person}_career_summary.txt", "w", encoding="utf-8") as f:
                f.write(career_summary)
            print("\nCareer summary saved to 'career_summary.txt'")
        else:
            print("Failed to generate career summary")
        
        print("\nStep 4: Cleaning up temporary files...")
        cleanup_images(image_paths)
        
        print("Process completed!")

if __name__ == "__main__":
    main_CS()