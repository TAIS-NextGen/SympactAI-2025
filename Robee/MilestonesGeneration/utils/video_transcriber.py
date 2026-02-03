import os
import sys
import json
import glob
import tempfile
import warnings
from pathlib import Path
import yt_dlp
import subprocess
import shutil
from pydub import AudioSegment
from groq import Groq
import re
from dotenv import load_dotenv
import langdetect
from langdetect import detect

class VideoTranscriber:
    def __init__(self, api_key=None, language='auto'):
        """
        Initialize the VideoTranscriber
        
        Args:
            api_key (str, optional): Groq API key. If None, will load from .env file
            language (str): 'en' for English, 'ar' for Arabic, 'auto' for automatic detection
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please provide it as parameter or set GROQ_API_KEY in .env file")
        
        self.client = Groq(api_key=api_key)
        self.language = language
        self.videos_dir = "./MilestonesGeneration/Videos"
        
        # Create videos directory if it doesn't exist
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def download_video_audio(self, url):
        """
        Download audio from YouTube video
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            tuple: (video_id, title, audio_file_path)
        """
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': f'{self.videos_dir}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }]
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info first
            video_info = ydl.extract_info(url, download=False)
            video_id = video_info['id']
            title = video_info.get('title', 'Unknown Title')
            
            print(f"Video Title: {title}")
            print(f"Video ID: {video_id}")
            
            # Download the audio
            ydl.download([url])
            
            audio_file_path = Path(f"{self.videos_dir}/{video_id}.wav")
            
            return video_id, title, audio_file_path
    
    def detect_language_from_sample(self, audio_file_path):
        """
        Detect language by transcribing a small sample of the audio
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Detected language ('en' or 'ar')
        """
        try:
            # Load audio and take first 30 seconds for language detection
            audio = AudioSegment.from_file(audio_file_path)
            sample = audio[:30000]  # First 30 seconds
            
            # Save sample to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sample.export(temp_file.name, format="wav")
                
                # Transcribe sample
                with open(temp_file.name, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=file,
                        model="distil-whisper-large-v3-en",
                        response_format="text",
                        temperature=0.0
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                # Detect language from transcription
                if transcription and len(transcription.strip()) > 10:
                    detected_lang = detect(transcription)
                    print(f"Detected language: {detected_lang}")
                    
                    # Map detected language to our supported languages
                    if detected_lang in ['ar', 'fa', 'ur']:  # Arabic and related languages
                        return 'ar'
                    else:
                        return 'en'
                else:
                    print("Could not detect language from sample, defaulting to English")
                    return 'en'
                    
        except Exception as e:
            print(f"Language detection failed: {e}. Defaulting to English")
            return 'en'
    
    def split_audio(self, file_path, chunk_length_ms=100000):
        """
        Split audio file into smaller chunks for large files
        
        Args:
            file_path (str): Path to audio file
            chunk_length_ms (int): Length of each chunk in milliseconds
            
        Returns:
            list: List of audio chunks
        """
        audio = AudioSegment.from_file(file_path)
        chunks = []
        
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunks.append(chunk)
        
        return chunks
    
    def transcribe_english_audio(self, filename):
        """
        Transcribe English audio using Groq API
        
        Args:
            filename (str): Path to audio file
            
        Returns:
            str: Transcribed text
        """
        # Check file size (Groq has a 25MB limit)
        file_size = os.path.getsize(filename)
        max_size = 25 * 1024 * 1024  # 25MB in bytes
        
        if file_size <= max_size:
            # File is small enough, transcribe directly
            try:
                with open(filename, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=file,
                        model="distil-whisper-large-v3-en",
                        response_format="text",
                        language="en",
                        temperature=0.0
                    )
                    return transcription
            except Exception as e:
                print(f"Direct transcription failed: {e}")
                return self._transcribe_with_chunking(filename)
        else:
            return self._transcribe_with_chunking(filename)
    
    def _transcribe_with_chunking(self, filename):
        """
        Transcribe large audio files by splitting into chunks
        
        Args:
            filename (str): Path to audio file
            
        Returns:
            str: Combined transcribed text
        """
        print(f"File too large, splitting into chunks...")
        
        chunks = self.split_audio(filename)
        all_transcriptions = []
        
        for i, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                chunk.export(temp_file.name, format="wav")
                
                try:
                    with open(temp_file.name, "rb") as file:
                        transcription = self.client.audio.transcriptions.create(
                            file=file,
                            model="distil-whisper-large-v3-en",
                            response_format="text",
                            language="en",
                            temperature=0.0
                        )
                        all_transcriptions.append(transcription)
                        print(f"Processed chunk {i+1}/{len(chunks)}")
                except Exception as e:
                    print(f"Error transcribing chunk {i+1}: {e}")
                    all_transcriptions.append(f"[Error in chunk {i+1}]")
                
                os.unlink(temp_file.name)
        
        return " ".join(all_transcriptions)
    
    def transcribe_arabic_audio(self, filename):
        """
        Transcribe Arabic audio using Vosk (offline) - placeholder implementation
        Note: This would require Vosk model setup for Arabic
        
        Args:
            filename (str): Path to audio file
            
        Returns:
            str: Transcribed text in Arabic
        """
        # This is a simplified version - you would need to implement
        # the full Vosk Arabic transcription as in your original code
        print("Arabic transcription requires Vosk model setup...")
        return "Arabic transcription not fully implemented in this version"
    
    def process_arabic_text_with_groq(self, title, raw_transcription):
        """
        Process and improve Arabic transcription using Groq
        
        Args:
            title (str): Video title
            raw_transcription (str): Raw transcription text
            
        Returns:
            tuple: (arabic_improved, english_translation)
        """
        # Split text if too long
        if len(raw_transcription) <= 4500:
            # Process directly
            arabic_improved = self._process_arabic_chunk(title, raw_transcription)
        else:
            # Split and process in chunks
            chunks = self._split_text_with_overlap(raw_transcription)
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                print(f"Processing Arabic chunk {i+1}/{len(chunks)}...")
                processed_chunk = self._process_arabic_chunk(title, chunk, i+1, len(chunks))
                processed_chunks.append(processed_chunk)
            
            # Merge chunks
            arabic_improved = self._merge_arabic_chunks(title, processed_chunks)
        
        # Translate to English
        english_translation = self._translate_to_english(arabic_improved)
        
        return arabic_improved, english_translation
    
    def _process_arabic_chunk(self, title, chunk, chunk_num=1, total_chunks=1):
        """Process a single Arabic text chunk"""
        chunk_info = f" (هذا جزء {chunk_num} من {total_chunks})" if total_chunks > 1 else ""
        
        prompt = (
            "حوّل هذا النص المنقول من خطاب إلى نص مترابط، منظم، وواضح. "
            "رتب الأفكار، صحح الأخطاء اللغوية إن وجدت، وحافظ على المعنى الأصلي دون تحريف. "
            "يُمنع حذف أو إسقاط أي فكرة واردة في النص الأصلي، بل يجب إعادة صياغتها وتنظيمها فقط. "
            "يجب أن تكون النتيجة مكتوبة كلها باللغة العربية، بما في ذلك الأرقام إن وُجدت"
            f"{chunk_info}:\n\n"
            f"[العنوان]: {title}\n\n"
            f"[النص المنقول]: {chunk}\n\n"
        )
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0,
            seed=2025
        )
        
        return response.choices[0].message.content
    
    def _split_text_with_overlap(self, text, max_length=4000, overlap=200):
        """Split text into overlapping chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_length, len(text))
            
            if end < len(text):
                # Try to break at sentence endings
                sentence_endings = ['.', '!', '?', '؟', '۔']
                break_point = end
                
                for i in range(end - 1, max(start + max_length // 2, start), -1):
                    if text[i] in sentence_endings and i + 1 < len(text) and text[i + 1] == ' ':
                        break_point = i + 1
                        break
                
                if break_point == end:
                    for i in range(end - 1, max(start + max_length // 2, start), -1):
                        if text[i] == ' ':
                            break_point = i
                            break
                
                end = break_point
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
        
        return chunks
    
    def _merge_arabic_chunks(self, title, processed_chunks):
        """Merge processed Arabic chunks"""
        if len(processed_chunks) == 1:
            return processed_chunks[0]
        
        combined_text = "\n\n".join(processed_chunks)
        
        merge_prompt = (
            "قم بدمج هذه النصوص المعالجة في نص واحد متماسك ومترابط. "
            "احذف التكرار، ونسق الأفكار، وتأكد من التدفق الطبيعي للنص. "
            "حافظ على جميع الأفكار والمعلومات المهمة دون حذف. "
            "يجب أن تكون النتيجة نصاً واحداً مترابطاً وسلساً باللغة العربية:\n\n"
            f"[العنوان]: {title}\n\n"
            f"[النصوص المعالجة للدمج]:\n{combined_text}\n\n"
        )
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": merge_prompt}],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0,
            seed=2025
        )
        
        return response.choices[0].message.content
    
    def _translate_to_english(self, arabic_text):
        """Translate Arabic text to English"""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Translate this text from Arabic to English without changing the meaning and without dropping any ideas:\n\n{arabic_text}"
            }],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0,
            seed=2025
        )
        
        return response.choices[0].message.content
    
    def save_results(self, video_id, title, transcription, language_suffix=""):
        """
        Save transcription and title to text files
        
        Args:
            video_id (str): Video ID
            title (str): Video title
            transcription (str): Transcribed text
            language_suffix (str): Language suffix for filename
        """
        # Save title
        title_file = os.path.join(self.videos_dir, f"{video_id}_title{language_suffix}.txt")
        with open(title_file, "w", encoding="utf-8") as f:
            f.write(title)
        
        # Save transcription
        transcription_file = os.path.join(self.videos_dir, f"{video_id}_transcription{language_suffix}.txt")
        with open(transcription_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        print(f"Saved title to: {title_file}")
        print(f"Saved transcription to: {transcription_file}")
        
        return title_file, transcription_file
    
    def process_video(self, url):
        """
        Main method to process a video URL and generate transcription
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            dict: Results containing file paths and content
        """
        try:
            # Download video audio
            print("Downloading video audio...")
            video_id, title, audio_file_path = self.download_video_audio(url)
            
            # Detect language if set to auto
            detected_language = self.language
            if self.language == 'auto':
                print("Detecting language from audio sample...")
                detected_language = self.detect_language_from_sample(str(audio_file_path))
                print(f"Language detected: {'Arabic' if detected_language == 'ar' else 'English'}")
            
            if detected_language == 'en':
                # English transcription
                print("Transcribing English audio...")
                transcription = self.transcribe_english_audio(str(audio_file_path))
                
                # Save results
                title_file, transcription_file = self.save_results(video_id, title, transcription)
                
                return {
                    'success': True,
                    'video_id': video_id,
                    'title': title,
                    'transcription': transcription,
                    'title_file': title_file,
                    'transcription_file': transcription_file,
                    'language': 'english',
                    'detected_language': detected_language
                }
                
            elif detected_language == 'ar':
                # Arabic transcription (would need full Vosk implementation)
                print("Processing Arabic audio...")
                
                # This is a placeholder - you'd need to implement the full Vosk Arabic transcription
                raw_transcription = "Arabic transcription placeholder - implement Vosk Arabic model"
                
                # Process with Groq
                arabic_improved, english_translation = self.process_arabic_text_with_groq(title, raw_transcription)
                
                # Save Arabic results
                title_file_ar, transcription_file_ar = self.save_results(video_id, title, arabic_improved, "_arabic")
                
                # Save English translation
                title_file_en, transcription_file_en = self.save_results(video_id, title, english_translation, "_english")
                
                return {
                    'success': True,
                    'video_id': video_id,
                    'title': title,
                    'arabic_transcription': arabic_improved,
                    'english_transcription': english_translation,
                    'title_file_ar': title_file_ar,
                    'transcription_file_ar': transcription_file_ar,
                    'title_file_en': title_file_en,
                    'transcription_file_en': transcription_file_en,
                    'language': 'arabic',
                    'detected_language': detected_language
                }
            
        except Exception as e:
            print(f"Error processing video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Clean up audio file
            if 'audio_file_path' in locals() and os.path.exists(audio_file_path):
                try:
                    os.remove(audio_file_path)
                    print(f"Cleaned up audio file: {audio_file_path}")
                except:
                    pass


# Example usage
if __name__ == "__main__":
    # API key will be loaded from .env file automatically
    # Create .env file with: GROQ_API_KEY=your_actual_api_key_here
    
    # Example for automatic language detection
    transcriber = VideoTranscriber(language='auto')  # Will auto-detect language
    result = transcriber.process_video("https://www.youtube.com/watch?v=example")
    
    if result['success']:
        print(f"Transcription completed!")
        print(f"Detected language: {result['detected_language']}")
        print(f"Title: {result['title']}")
        if result['language'] == 'english':
            print(f"Files saved: {result['title_file']}, {result['transcription_file']}")
        else:
            print(f"Arabic files: {result['title_file_ar']}, {result['transcription_file_ar']}")
            print(f"English files: {result['title_file_en']}, {result['transcription_file_en']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example for specific language (if you know the language beforehand)
    # transcriber_en = VideoTranscriber(language='en')
    # transcriber_ar = VideoTranscriber(language='ar')
