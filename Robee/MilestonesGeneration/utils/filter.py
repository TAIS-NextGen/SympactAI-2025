from MilestonesGeneration.utils.SandS import scrape_and_save
import openai
import os
import tiktoken
import time
from dotenv import load_dotenv
load_dotenv()

def count_tokens(text, model="gpt-4"):
    """Count tokens in text for a given model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chunk_text(text, max_tokens=6000, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    sentences = text.split('\n')
    
    for sentence in sentences:
        sentence_tokens = len(encoding.encode(sentence))
        
        if current_length + sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_tokens
            else:
                # Single sentence is too long, split it further
                words = sentence.split()
                temp_chunk = []
                temp_length = 0
                
                for word in words:
                    word_tokens = len(encoding.encode(word))
                    if temp_length + word_tokens > max_tokens:
                        if temp_chunk:
                            chunks.append(' '.join(temp_chunk))
                            temp_chunk = [word]
                            temp_length = word_tokens
                        else:
                            # Single word is too long, just add it
                            chunks.append(word)
                    else:
                        temp_chunk.append(word)
                        temp_length += word_tokens
                
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
        else:
            current_chunk.append(sentence)
            current_length += sentence_tokens
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def filter_info(scrape=False):
    print("Starting filtering process...")
    # Use environment variable for API key (more secure)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    if scrape:
        print('Scraping and saving data...')
        persons = scrape_and_save()
        print(f"Scraped and saved data for {len(persons)} persons.")
    else:
        persons = [d.split('.')[0] for d in os.listdir('./MilestonesGeneration/Persons')]
    
    for person in persons:
        print(f"Processing person: {person}")
        person_dir = f'./MilestonesGeneration/{person}' 
        if os.path.isdir(person_dir):
            for md_file in os.listdir(person_dir):
                if md_file.endswith('.md'):
                    md_path = os.path.join(person_dir, md_file)
                    
                    try:
                        with open(md_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        
                        # Check if content is too long
                        content_tokens = count_tokens(content)
                        print(f"Processing {md_path} - {content_tokens} tokens")
                        
                        if content_tokens > 6000:  # Leave room for system message and response
                            print(f"Content too long ({content_tokens} tokens), chunking...")
                            chunks = chunk_text(content, max_tokens=6000)
                            cleaned_chunks = []
                            
                            for i, chunk in enumerate(chunks):
                                print(f"Processing chunk {i+1}/{len(chunks)}")
                                
                                try:
                                    openai_response = openai.chat.completions.create(
                                        model="gpt-4",
                                        messages=[
                                            {"role": "system", "content": "You are a helpful assistant. Clean the content by removing links not related to resume and unnecessary lifestyle/career information. Keep professional and relevant information."},
                                            {"role": "user", "content": f"Clean this content chunk:\n\n{chunk}"}
                                        ],
                                        max_tokens=2000
                                    )
                                    
                                    cleaned_chunk = openai_response['choices'][0]['message']['content']
                                    cleaned_chunks.append(cleaned_chunk)
                                    
                                except Exception as e:
                                    print(f"Error processing chunk {i+1}: {e}")
                                    cleaned_chunks.append(chunk)  # Keep original if cleaning fails
                            
                            cleaned_content = '\n\n'.join(cleaned_chunks)
                        else:
                            # Content is short enough, process normally
                            try:
                                openai_response = openai.chat.completions.create(
model="gpt-4",
messages=[
    {
        "role": "system", 
        "content": """You are a professional resume editor. Your task is to extract and organize only career-relevant information from messy or unstructured content. 

Guidelines:
- Remove all non-professional links, social media references, and personal lifestyle content
- Keep only professional links (LinkedIn, portfolio, GitHub, company websites)
- Preserve ALL dates exactly as they appear - they are critical
- Remove images, photos, and visual elements
- Focus on: work experience, education, skills, certifications, achievements, projects
- Exclude: personal hobbies, social activities, non-professional interests
- Maintain chronological order and professional formatting
- Keep contact information if professional (email, phone, LinkedIn)"""
    },
    {
        "role": "user", 
        "content": f"""Clean and restructure this content into a professional resume format. 

CRITICAL REQUIREMENTS:
1. Preserve ALL dates exactly as written - do not modify or reformat dates
2. Remove non-professional links and personal lifestyle information
3. Keep only career-relevant content: jobs, education, skills, achievements
4. Remove images and unnecessary visual elements
5. Organize in standard resume sections: Contact, Summary, Experience, Education, Skills
6. Maintain professional tone throughout

Content to clean:
{content}"""
    }
],
max_tokens=2000
                                )
                                
                                cleaned_content = openai_response['choices'][0]['message']['content']
                                
                            except Exception as e:
                                print(f"Error processing {md_path}: {e}")
                                cleaned_content = content  # Keep original if cleaning fails
                        
                        # Save cleaned content
                        cleaned_path = md_path.rsplit('.', 1)[0] + '_cleaned.txt'
                        with open(cleaned_path, 'w', encoding='utf-8') as file:
                            file.write(cleaned_content)
                        
                        print(f"Cleaned content saved to: {cleaned_path}")
                        time.sleep(10)  
                    except Exception as e:
                        print(f"Error processing file {md_path}: {e}")
                        continue