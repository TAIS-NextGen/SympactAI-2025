import os
import json
import openai
from pathlib import Path
import time
from dotenv import load_dotenv
load_dotenv()

openai.api_key =  os.getenv('OPENAI_API_KEY') 

def read_person_files(person_name):
    person_dir = Path('./MilestonesGeneration/') / person_name
    files_content = {}
    
    if not person_dir.exists():
        print(f"Directory not found: {person_dir}")
        return files_content
    
    for file_path in person_dir.glob('*_cleaned.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                files_content[file_path.name] = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    career_summary_path = person_dir / f'{person_name}_career_summary.txt'
    if career_summary_path.exists():
        try:
            with open(career_summary_path, 'r', encoding='utf-8') as f:
                files_content['career_summary.txt'] = f.read()
        except Exception as e:
            print(f"Error reading career_summary.txt: {e}")
    
    return files_content

def truncate_content(content, max_chars=3000):
    if len(content) <= max_chars:
        return content
    
    sentences = content.split('.')
    truncated = ""
    for sentence in sentences:
        if len(truncated + sentence + ".") <= max_chars:
            truncated += sentence + "."
        else:
            break
    
    return truncated + "\n[Content truncated due to length...]"

def generate_roadmap_with_gpt(person_name, files_content):
    combined_content = f"Person: {person_name}\n\n"
    
    if 'career_summary.txt' in files_content:
        summary_content = truncate_content(files_content['career_summary.txt'], 2000)
        combined_content += f"--- career_summary.txt ---\n{summary_content}\n\n"
    
    remaining_space = 4000 - len(combined_content)
    other_files = {k: v for k, v in files_content.items() if k != 'career_summary.txt'}
    
    if other_files:
        space_per_file = remaining_space // len(other_files)
        for filename, content in other_files.items():
            truncated = truncate_content(content, space_per_file)
            combined_content += f"--- {filename} ---\n{truncated}\n\n"
    
    prompt = f"""Based on the following information about {person_name}, create a comprehensive career roadmap using ALL available information and reasonable inferences.

{combined_content}

Analyze this person's career journey and create a detailed roadmap showing their major goals/positions and ALL milestones that helped them reach each goal.

CRITICAL INSTRUCTIONS:
1. Extract ALL relevant information from the provided data
2. Create comprehensive milestone lists (aim for 6-12 milestones per goal when data supports it)
3. Include both explicit achievements and reasonable inferences from the career progression
4. Be thorough - don't miss educational, professional, or skill development milestones
5. IMPORTANT: Each goal should focus on ONE specific career objective - avoid using "and" in goal titles
6. If you identify combined objectives, split them into separate, focused goals
7. CRITICAL: Milestones must be PREREQUISITES or STEPS leading to the goal, NOT repetitions of the goal itself
8. Avoid circular milestones - if the goal is "Data Science Intern", don't create a milestone "Get Data Science Internship"

MILESTONE CATEGORIES TO EXTRACT AND INFER:

EDUCATIONAL MILESTONES:
- All degrees mentioned (Bachelor's, Master's, PhD with specific fields and institutions)
- Professional certifications and licenses
- Training programs, workshops, bootcamps
- Online courses and MOOCs completed
- Research publications and papers
- Academic projects and thesis work
- Conference presentations and talks
- Academic awards and scholarships
- Teaching or mentoring experience

PROFESSIONAL MILESTONES:
- All job positions and roles held
- Key projects and technical accomplishments
- Leadership roles and team management
- Technical skills development and frameworks learned
- Industry recognition and professional awards
- Professional network building and collaborations
- Mentorship received or given
- Cross-functional and international experience
- Entrepreneurial ventures and startups
- Consulting or freelance work

SKILL DEVELOPMENT MILESTONES:
- Programming languages and technologies mastered
- Technical frameworks and tools proficiency
- Soft skills development (communication, leadership)
- Language proficiency achievements
- Industry-specific expertise gained
- Platform and tool certifications

IMPORTANT GUIDELINES:
- Each goal should have 6-12 milestones (more if rich data, minimum 4-6 even with limited data)
- Extract every educational qualification, job, project, skill mentioned
- Infer logical prerequisite milestones for major achievements
- Be specific with actual names, institutions, companies, technologies
- Include foundational milestones that would be necessary for career progression
- Don't be overly conservative - if someone achieved something, include the likely steps
- AVOID REDUNDANCY: Milestones should be PREPARATION STEPS, not restatements of the goal
- Think: "What did they need to learn/do/achieve BEFORE reaching this goal?"

Return ONLY a valid JSON object in this format:
{{
  "roadmaps": {{
    "goal1": {{
      "title": "Data Science Intern",
      "duration": "6-12 months",
      "milestones": [
        {{"name": "Complete Bachelor's degree in Statistics", "score": 9}},
        {{"name": "Learn Python programming fundamentals", "score": 8}},
        {{"name": "Master pandas and numpy libraries", "score": 8}},
        {{"name": "Complete online machine learning course", "score": 7}},
        {{"name": "Build personal data science projects portfolio", "score": 8}},
        {{"name": "Gain experience with SQL databases", "score": 7}}
      ]
    }},
    "goal2": {{
      "title": "Research Scientist",
      "duration": "3-5 years", 
      "milestones": [
        {{"name": "Earn PhD in relevant field", "score": 10}},
        {{"name": "Publish research papers in peer-reviewed journals", "score": 9}},
        {{"name": "Present research at academic conferences", "score": 8}},
        {{"name": "Develop expertise in specialized research methods", "score": 8}},
        {{"name": "Collaborate with industry partners on projects", "score": 7}},
        {{"name": "Secure research funding or grants", "score": 7}},
        {{"name": "Mentor graduate students or junior researchers", "score": 6}},
        {{"name": "Build network within research community", "score": 6}}
      ]
    }}
  }}
}}

Rules:
- Create 3-5 goals based on career progression
- Each goal should be a SINGLE, specific career objective or position - avoid using "and" in goal titles
- If you identify multiple objectives, create separate goals for each one
- Goal titles should be concise and focused (e.g., "Software Engineer at XYZ Corp", "Research Scientist at ABC University", "Team Lead at DEF Inc.")
- Never forget the goal location when mentioning the goal dontg ive general goals like "Engineering Intern" but specify the company or institution if available
- Each goal should have 6-12 comprehensive milestones
- Never put a milestone that have not been achieved by the person or not given in the context related to the person
- Never put a milestone to a goal that happened after the goal was achieved you should consider some temporal and logic relationships that should be got from the person's context
- Milestones must be PREREQUISITE STEPS that lead to achieving the goal, not repetitions of the goal AND this is the most important part to determine
- Milestones should be specific actions, achievements, or qualifications that are necessary to reach the goal
- Never put for a goal a milestone that is the goal itself for exemple if we have a goal "Data Science Intern" we should never put "Hold a Data Science Internship" as a milestone
- Think: "What skills, education, experience are needed BEFORE someone can get this position?"
- Be thorough in extracting all achievements, qualifications, and experiences
- Include both explicit mentions and reasonable career progression inferences
- Score should be 1-10 indicating importance (10 being most critical)
- Use specific names, institutions, technologies when available
- Return only valid JSON, no additional text"""

    try:
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a thorough career analyst that creates comprehensive roadmaps by extracting ALL available information and making reasonable inferences. Be thorough - aim for 6-12 milestones per goal. Extract every qualification, job, project, and skill mentioned. CRITICAL: Milestones must be PREREQUISITES/PREPARATION STEPS for the goal, never repetitions of the goal itself. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.1
        )
        
        response_content = response.choices[0].message.content.strip()
        
        if not response_content:
            print(f"Empty response for {person_name}")
            return None
            
        if response_content.startswith("```json"):
            response_content = response_content.replace("```json", "").replace("```", "").strip()
        
        return response_content
    
    except Exception as e:
        print(f"Error calling OpenAI API for {person_name}: {e}")
        return None

def process_all_persons():
    persons_dir = Path('./MilestonesGeneration/Persons/names')
    if not persons_dir.exists():
        print("Persons directory not found!")
        return
    
    persons = [d.split('.')[0] for d in os.listdir('./MilestonesGeneration/Persons/names')]
    
    results = {}
    
    for person in persons:
        print(f"Processing {person}...")
        
        files_content = read_person_files(person)
        
        if not files_content:
            print(f"No relevant files found for {person}")
            continue
        
        roadmap_json = generate_roadmap_with_gpt(person, files_content)
        
        if roadmap_json:
            try:
                roadmap_data = json.loads(roadmap_json)
                results[person] = roadmap_data
                print(f"Successfully processed {person}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON for {person}: {e}")
                print(f"Raw response: {roadmap_json[:200]}...")
                results[person] = {"error": "Invalid JSON", "raw_response": roadmap_json}
        else:
            print(f"Failed to generate roadmap for {person}")
        
        time.sleep(2)
    
    return results

def save_results(results, output_file='roadmaps_output.json'):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    print("Starting person files to roadmap conversion...")
    
    results = process_all_persons()
    
    if results:
        save_results(results)
        
        print(f"\n=== SUMMARY ===")
        print(f"Total persons processed: {len(results)}")
        successful = sum(1 for r in results.values() if 'error' not in r)
        print(f"Successful conversions: {successful}")
        print(f"Failed conversions: {len(results) - successful}")
        
        if successful > 0:
            example_person = next(person for person, data in results.items() if 'error' not in data)
            print(f"\nExample result for {example_person}:")
            print(json.dumps(results[example_person], indent=2)[:500] + "...")
    else:
        print("No results generated.")

if __name__ == "__main__":
    main()