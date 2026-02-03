import asyncio
import time
import os
import glob
from pathlib import Path
from MilestonesGeneration.utils.scrape_page import main
from dotenv import load_dotenv
load_dotenv()

def scrape_and_save():
    persons = list()
    for txt_file in glob.glob('./MilestonesGeneration/Persons/names/*.txt'):
        print(txt_file)
        with open(txt_file, 'r', encoding='utf-8') as file:
            web_urls = file.read().strip()
            for single_url in web_urls.splitlines():
                print(f"Processing: {single_url}")
                content = asyncio.run(main(single_url))
                if content:
                    # Fixed: Use pathlib for better path handling
                    txt_path = Path(txt_file)
                    # Create directory based on the txt filename without extension
                    mkdir = txt_path.stem
                    persons.append(mkdir)
                    output_dir = Path('./MilestonesGeneration/') / mkdir
                    
                    # Create directory if it doesn't exist
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create output filename
                    domain = single_url.split('//')[-1].split('/')[0]
                    filename = output_dir / f"{domain}.md"
                    
                    # Write content to file
                    with open(filename, 'w', encoding='utf-8') as output_file:
                        output_file.write(content)
                    
                    print(f"Saved: {filename}")
                else:
                    print(f"No content retrieved for: {single_url}")
                
                time.sleep(10)
    return list(set(persons))