# import sys
# import warnings
# import whisper
# from pathlib import Path
# import yt_dlp
# import subprocess
# import torch
# import shutil
# import numpy as np

# if arabic : 
#     def process_video(URL):
#     Type = "Youtube video or playlist"
#     ids = URL.split('=')[-1].strip()
#     video_path = URL
#     video_path_local_list = []

#     if Type == "Youtube video or playlist":
#         ydl_opts = {
#             'format': 'm4a/bestaudio/best',
#             'outtmpl': './MilestonesGeneration/Videos/%(id)s.%(ext)s',  
#             'postprocessors': [{  
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'wav',
#             }]
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             error_code = ydl.download([URL])
            
#             video_info = ydl.extract_info(URL, download=False)

#             title = video_info.get('title', 'Unknown Title')
#             print("Video Title:", title)

#             video_path_local_list.append(Path(f"./MilestonesGeneration/Videos/{video_info['id']}.wav"))

# !sudo apt-get install git-lfs
# !git lfs install

# !git clone https://huggingface.co/linagora/linto-asr-ar-tn-0.1.git

# %cd linto-asr-ar-tn-0.1


# !mkdir dir_for_zip_extract

# !unzip ./MilestonesGeneration/Videos/vosk-model.zip -d dir_for_zip_extract


# from pydub import AudioSegment

# audio = AudioSegment.from_file(f"./MilestonesGeneration/Videos/{ids}.wav")  

# audio = audio.set_channels(1)
# audio = audio.set_sample_width(2)
# audio = audio.set_frame_rate(16000)

# # Export to WAV (PCM)
# audio.export("./MilestonesGeneration/Videos/converted_audio.wav", format="wav")

# from IPython.display import display, Markdown, YouTubeVideo
# from vosk import Model, KaldiRecognizer
# import wave
# import json
# import os
# import math
# def split_wav_file(input_file, output_dir, chunk_duration=60, overlap_duration=5):
#     """
#     Split a WAV file into overlapping chunks of specified duration (in seconds)
    
#     Args:
#         input_file: Path to input WAV file
#         output_dir: Directory to save chunks
#         chunk_duration: Duration of each chunk in seconds (default: 60)
#         overlap_duration: Overlap between chunks in seconds (default: 5)
    
#     Returns:
#         List of chunk file paths with their time ranges
#     """
#     os.makedirs(output_dir, exist_ok=True)
    
#     chunk_info = []
    
#     with wave.open(input_file, 'rb') as wf:
#         frames_per_second = wf.getframerate()
#         total_frames = wf.getnframes()
#         total_duration = total_frames / frames_per_second
        
#         frames_per_chunk = frames_per_second * chunk_duration
#         frames_overlap = frames_per_second * overlap_duration
        
#         step_frames = frames_per_chunk - frames_overlap
        
#         num_chunks = math.ceil((total_frames - frames_overlap) / step_frames) if total_frames > frames_per_chunk else 1
        
#         print(f"Total duration: {total_duration:.2f} seconds")
#         print(f"Chunk duration: {chunk_duration}s with {overlap_duration}s overlap")
#         print(f"Number of chunks: {num_chunks}")
        
#         for i in range(num_chunks):
#             start_frame = i * step_frames
#             end_frame = min(start_frame + frames_per_chunk, total_frames)
            
#             start_time = start_frame / frames_per_second
#             end_time = end_frame / frames_per_second
            
#             chunk_filename = f"chunk_{i+1:03d}_{start_time:.1f}s-{end_time:.1f}s.wav"
#             chunk_path = os.path.join(output_dir, chunk_filename)
            
#             wf.setpos(start_frame)
            
#             chunk_frames = wf.readframes(end_frame - start_frame)
            
#             with wave.open(chunk_path, 'wb') as chunk_wf:
#                 chunk_wf.setnchannels(wf.getnchannels())
#                 chunk_wf.setsampwidth(wf.getsampwidth())
#                 chunk_wf.setframerate(wf.getframerate())
#                 chunk_wf.writeframes(chunk_frames)
            
#             chunk_info.append({
#                 'path': chunk_path,
#                 'start_time': start_time,
#                 'end_time': end_time,
#                 'filename': chunk_filename
#             })
            
#             print(f"Created chunk {i+1}/{num_chunks}: {chunk_filename} ({start_time:.1f}s - {end_time:.1f}s)")
    
#     return chunk_info

# def remove_overlap_from_transcript(transcript, is_first_chunk, is_last_chunk, overlap_ratio=0.1):
#     """
#     Remove overlapping content from transcript to avoid duplication
    
#     Args:
#         transcript: The transcript text
#         is_first_chunk: Whether this is the first chunk
#         is_last_chunk: Whether this is the last chunk
#         overlap_ratio: Ratio of transcript to consider as overlap (default: 0.1 = 10%)
    
#     Returns:
#         Cleaned transcript text
#     """
#     if not transcript.strip():
#         return transcript
    
#     words = transcript.split()
#     if len(words) <= 2:
#         return transcript
    
#     overlap_words = max(1, int(len(words) * overlap_ratio))
    
#     if not is_first_chunk:
#         words = words[overlap_words:]
    
#     if not is_last_chunk and len(words) > overlap_words:
#         words = words[:-overlap_words]
    
#     return " ".join(words)
#     """
#     Transcribe a single WAV file chunk
    
#     Args:
#         model: Vosk model object
#         audio_file: Path to WAV file
    
#     Returns:
#         Transcript text
#     """
#     with wave.open(audio_file, "rb") as wf:
#         if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
#             raise ValueError(f"Audio file {audio_file} must be WAV format mono PCM.")
        
#         rec = KaldiRecognizer(model, wf.getframerate())
        
#         chunk_size = 4000
#         transcript_parts = []
        
#         while True:
#             data = wf.readframes(chunk_size)
#             if len(data) == 0:
#                 break
            
#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())
#                 if result["text"]:
#                     transcript_parts.append(result["text"])
        
#         final_result = json.loads(rec.FinalResult())
#         if final_result["text"]:
#             transcript_parts.append(final_result["text"])
        
#         return " ".join(transcript_parts)

# def transcribe_wav_chunk(model, audio_file):
#     """
#     Transcribe a single WAV file chunk
    
#     Args:
#         model: Vosk model object
#         audio_file: Path to WAV file
    
#     Returns:
#         Transcript text
#     """
#     with wave.open(audio_file, "rb") as wf:
#         if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
#             raise ValueError(f"Audio file {audio_file} must be WAV format mono PCM.")
        
#         rec = KaldiRecognizer(model, wf.getframerate())
        
#         chunk_size = 4000
#         transcript_parts = []
        
#         while True:
#             data = wf.readframes(chunk_size)
#             if len(data) == 0:
#                 break
            
#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())
#                 if result["text"]:
#                     transcript_parts.append(result["text"])
        
#         # Get final result
#         final_result = json.loads(rec.FinalResult())
#         if final_result["text"]:
#             transcript_parts.append(final_result["text"])
        
#         return " ".join(transcript_parts)
# def get_transcript():
#     model_dir = "./MilestonesGeneration/Videos/linto-asr-ar-tn-0.1/dir_for_zip_extract/vosk-model"
#     audio_file = "./MilestonesGeneration/Videos/converted_audio.wav"
#     chunks_dir = "./MilestonesGeneration/Videos/audio_chunks"
#     chunk_duration = 60  
#     overlap_duration = 5 
    
#     print("Loading Vosk model...")
#     model = Model(model_dir)
#     print("Model loaded successfully!")
    
#     print("\nSplitting audio file...")
#     chunk_info = split_wav_file(audio_file, chunks_dir, chunk_duration, overlap_duration)
#     print("\nTranscribing chunks...")
#     full_transcript = []
#     raw_transcripts = [] 
    
#     for i, chunk in enumerate(chunk_info, 1):
#         chunk_file = chunk['path']
#         start_time = chunk['start_time']
#         end_time = chunk['end_time']
        
#         print(f"\nTranscribing chunk {i}/{len(chunk_info)}: {chunk['filename']}")
#         print(f"Time range: {start_time:.1f}s - {end_time:.1f}s")
        
#         try:
#             raw_transcript = transcribe_wav_chunk(model, chunk_file)
#             raw_transcripts.append(raw_transcript)
            
#             if raw_transcript.strip():
#                 is_first_chunk = (i == 1)
#                 is_last_chunk = (i == len(chunk_info))
                
#                 cleaned_transcript = remove_overlap_from_transcript(
#                     raw_transcript, is_first_chunk, is_last_chunk
#                 )
                
#                 print(f"Raw transcript: {raw_transcript}")
#                 if cleaned_transcript != raw_transcript:
#                     print(f"Cleaned transcript: {cleaned_transcript}")
                
#                 if cleaned_transcript.strip():
#                     full_transcript.append(cleaned_transcript)
#                 else:
#                     print(f"Chunk {i}: Transcript empty after overlap removal")
#             else:
#                 print(f"Chunk {i}: No speech detected")
                
#         except Exception as e:
#             print(f"Error transcribing chunk {i}: {str(e)}")
#             full_transcript.append(f"(Error in chunk {i}: {str(e)})")
    
#     transcript_file = "./MilestonesGeneration/Videos/complete_transcript.txt"
#     raw_transcript_file = "./MilestonesGeneration/Videos/raw_transcript_with_overlaps.txt"
    
#     final_transcript = " ".join(full_transcript)
#     with open(transcript_file, "w", encoding="utf-8") as f:
#         f.write(final_transcript)
    
#     with open(raw_transcript_file, "w", encoding="utf-8") as f:
#         for i, raw_transcript in enumerate(raw_transcripts, 1):
#             chunk = chunk_info[i-1]
#             f.write(f"[Chunk {i}] ({chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s)\n")
#             f.write(f"{raw_transcript}\n\n")
    
#     print(f"\n{'='*50}")
#     print("COMPLETE TRANSCRIPT:")
#     print(f"{'='*50}")
#     print(final_transcript)
    
#     print(f"\nFinal transcript saved to: {transcript_file}")
#     print(f"Raw transcripts (with overlaps) saved to: {raw_transcript_file}")
#     print(f"Audio chunks saved to: {chunks_dir}")
#     print(f"\nProcessed {len(chunk_info)} overlapping chunks with {overlap_duration}s overlap")

# get_transcript()
# with open('./MilestonesGeneration/Videos/raw_transcript_with_overlaps.txt' , 'r') as f  : 
#     transcription = f.read()
# from kaggle_secrets import UserSecretsClient
# user_secrets = UserSecretsClient()
# api_key = user_secrets.get_secret("groq")
# %%capture
# !pip install groq
# # from groq import Groq
# # import os

# # client = Groq(
# #     api_key=api_key  
# # )

# # chat_completion = client.chat.completions.create(
# #     messages=[
# #     {
# #         "role": "user",
# #         "content": (
# #             "حوّل هذا النص المنقول من خطاب إلى نص مترابط، منظم، وواضح. "
# #             "رتب الأفكار، صحح الأخطاء اللغوية إن وجدت، وحافظ على المعنى الأصلي دون تحريف. "
# #             "يُمنع حذف أو إسقاط أي فكرة واردة في النص الأصلي، بل يجب إعادة صياغتها وتنظيمها فقط. "
# #             "يجب أن تكون النتيجة مكتوبة كلها باللغة العربية، بما في ذلك الأرقام إن وُجدت:\n\n"
# #             f"[العنوان]: {title}\n\n"
# #             f"[النص المنقول]: {transcription}\n\n"
# #         )
# #     }
# #     ], 
# #     model="meta-llama/llama-4-maverick-17b-128e-instruct",
# #     temperature=0,
# #     seed=2025
# # )

# # # Print the merged result
# # arabic_transcription = chat_completion.choices[0].message.content
# # print(arabic_transcription)
# from groq import Groq
# import os
# import re

# def split_text_with_overlap(text, max_length=4000, overlap=200):
#     """
#     Split text into chunks with overlap, trying to break at sentence boundaries
#     """
#     if len(text) <= max_length:
#         return [text]
    
#     chunks = []
#     start = 0
    
#     while start < len(text):
#         # Calculate end position
#         end = min(start + max_length, len(text))
        
#         # If this isn't the last chunk, try to find a good breaking point
#         if end < len(text):
#             # Look for sentence endings in Arabic (periods, question marks, exclamation marks)
#             sentence_endings = ['.', '!', '?', '؟', '۔']
            
#             # Search backwards from the end position for a sentence ending
#             break_point = end
#             for i in range(end - 1, max(start + max_length // 2, start), -1):
#                 if text[i] in sentence_endings and i + 1 < len(text) and text[i + 1] == ' ':
#                     break_point = i + 1
#                     break
            
#             # If no sentence ending found, look for space
#             if break_point == end:
#                 for i in range(end - 1, max(start + max_length // 2, start), -1):
#                     if text[i] == ' ':
#                         break_point = i
#                         break
            
#             end = break_point
        
#         chunk = text[start:end].strip()
#         if chunk:
#             chunks.append(chunk)
        
#         # Move start position (with overlap)
#         if end >= len(text):
#             break
#         start = max(end - overlap, start + 1)
    
#     return chunks

# def process_text_chunk(client, title, chunk, chunk_index, total_chunks):
#     """
#     Process a single chunk of text
#     """
#     # Modify prompt slightly for chunks
#     chunk_prompt = (
#         "حوّل هذا النص المنقول من خطاب إلى نص مترابط، منظم، وواضح. "
#         "رتب الأفكار، صحح الأخطاء اللغوية إن وجدت، وحافظ على المعنى الأصلي دون تحريف. "
#         "يُمنع حذف أو إسقاط أي فكرة واردة في النص الأصلي، بل يجب إعادة صياغتها وتنظيمها فقط. "
#         "يجب أن تكون النتيجة مكتوبة كلها باللغة العربية، بما في ذلك الأرقام إن وُجدت"
#     )
    
#     if total_chunks > 1:
#         chunk_prompt += f" (هذا جزء {chunk_index + 1} من {total_chunks})"
    
#     chunk_prompt += f":\n\n[العنوان]: {title}\n\n[النص المنقول]: {chunk}\n\n"
    
#     chat_completion = client.chat.completions.create(
#         messages=[{
#             "role": "user",
#             "content": chunk_prompt
#         }], 
#         model="meta-llama/llama-4-maverick-17b-128e-instruct",
#         temperature=0,
#         seed=2025
#     )
    
#     return chat_completion.choices[0].message.content

# def merge_processed_chunks(client, title, processed_chunks):
#     """
#     Merge processed chunks into a coherent final text
#     """
#     if len(processed_chunks) == 1:
#         return processed_chunks[0]
    
#     # Combine all processed chunks
#     combined_text = "\n\n".join(processed_chunks)
    
#     # Create a merging prompt
#     merge_prompt = (
#         "قم بدمج هذه النصوص المعالجة في نص واحد متماسك ومترابط. "
#         "احذف التكرار، ونسق الأفكار، وتأكد من التدفق الطبيعي للنص. "
#         "حافظ على جميع الأفكار والمعلومات المهمة دون حذف. "
#         "يجب أن تكون النتيجة نصاً واحداً مترابطاً وسلساً باللغة العربية:\n\n"
#         f"[العنوان]: {title}\n\n"
#         f"[النصوص المعالجة للدمج]:\n{combined_text}\n\n"
#     )
    
#     chat_completion = client.chat.completions.create(
#         messages=[{
#             "role": "user",
#             "content": merge_prompt
#         }], 
#         model="meta-llama/llama-4-maverick-17b-128e-instruct",
#         temperature=0,
#         seed=2025
#     )
    
#     return chat_completion.choices[0].message.content

# def process_arabic_transcription(api_key, title, transcription, max_chunk_length=4000):
#     """
#     Main function to process Arabic transcription with chunking if needed
#     """
#     client = Groq(api_key=api_key)
    
#     # Check if text needs to be split
#     if len(transcription) <= 4500:
#         # Process normally for short texts
#         chat_completion = client.chat.completions.create(
#             messages=[{
#                 "role": "user",
#                 "content": (
#                     "حوّل هذا النص المنقول من خطاب إلى نص مترابط، منظم، وواضح. "
#                     "رتب الأفكار، صحح الأخطاء اللغوية إن وجدت، وحافظ على المعنى الأصلي دون تحريف. "
#                     "يُمنع حذف أو إسقاط أي فكرة واردة في النص الأصلي، بل يجب إعادة صياغتها وتنظيمها فقط. "
#                     "يجب أن تكون النتيجة مكتوبة كلها باللغة العربية، بما في ذلك الأرقام إن وُجدت:\n\n"
#                     f"[العنوان]: {title}\n\n"
#                     f"[النص المنقول]: {transcription}\n\n"
#                 )
#             }], 
#             model="meta-llama/llama-4-maverick-17b-128e-instruct",
#             temperature=0,
#             seed=2025
#         )
#         return chat_completion.choices[0].message.content
    
#     else:
#         # Split text into chunks with overlap
#         print(f"Text length ({len(transcription)}) exceeds 4500 characters. Splitting into chunks...")
#         chunks = split_text_with_overlap(transcription, max_chunk_length)
#         print(f"Split into {len(chunks)} chunks")
        
#         # Process each chunk
#         processed_chunks = []
#         for i, chunk in enumerate(chunks):
#             print(f"Processing chunk {i + 1}/{len(chunks)}...")
#             processed_chunk = process_text_chunk(client, title, chunk, i, len(chunks))
#             processed_chunks.append(processed_chunk)
        
#         # Merge processed chunks
#         print("Merging processed chunks...")
#         final_result = merge_processed_chunks(client, title, processed_chunks)
        
#         return final_result
# arabic_transcription = process_arabic_transcription(api_key, title, transcription)
# print(arabic_transcription)

# client = Groq(
#     api_key=api_key
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": (
#                 f"Translate this text from Arabic to English without changing the meaning "
#                 f"and without dropping any ideas:\n\n{arabic_transcription}"
#             )
#         }
#     ],
#     model="meta-llama/llama-4-maverick-17b-128e-instruct",
#     temperature=0,
#     seed=2025
# )

# translated_text = chat_completion.choices[0].message.content
# print(translated_text)

# directory = "./MilestonesGeneration/Videos"
# file_path = os.path.join(directory, "final_transcription.txt")

# os.makedirs(directory, exist_ok=True)

# with open(file_path, "w", encoding="utf-8") as file:
#     file.write(translated_text)

# print(f"File saved to {file_path}")

# else : 

# def process_video(URL) : 
#     Type = "Youtube video or playlist"
#     ids = URL.split('=')[-1].strip()
#     video_path = URL
#     video_path_local_list = []

#     if Type == "Youtube video or playlist":
#         ydl_opts = {
#             'format': 'm4a/bestaudio/best',
#             'outtmpl': './MilestonesGeneration/Videos/%(id)s.%(ext)s',  
#             'postprocessors': [{  
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'wav',
#             }]
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             error_code = ydl.download([URL])
            
#             video_info = ydl.extract_info(URL, download=False)

#             title = video_info.get('title', 'Unknown Title')
#             print("Video Title:", title)

#             video_path_local_list.append(Path(f"./MilestonesGeneration/Videos/{video_info['id']}.wav"))


# Type = "Youtube video or playlist"
# URL = "https://www.youtube.com/watch?v=Tpv6M6MmkE8"
# ids = URL.split('=')[-1].strip()
# video_path = URL
# video_path_local_list = []

# if Type == "Youtube video or playlist":
#     ydl_opts = {
#         'format': 'm4a/bestaudio/best',
#         'outtmpl': './MilestonesGeneration/Videos/%(id)s.%(ext)s',  
#         'postprocessors': [{  
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'wav',
#         }]
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         error_code = ydl.download([URL])
        
#         video_info = ydl.extract_info(URL, download=False)

#         title = video_info.get('title', 'Unknown Title')
#         print("Video Title:", title)

#         video_path_local_list.append(Path(f"./MilestonesGeneration/Videos/{video_info['id']}.wav"))

# import os
# import json
# from groq import Groq
# from pydub import AudioSegment
# import tempfile

# # Initialize the Groq client
# client = Groq(
#     api_key=secret_value_0
# )

# def split_audio(file_path, chunk_length_ms=100000):  
#     """Split audio file into smaller chunks"""
#     audio = AudioSegment.from_file(file_path)
#     chunks = []
    
#     for i in range(0, len(audio), chunk_length_ms):
#         chunk = audio[i:i + chunk_length_ms]
#         chunks.append(chunk)
    
#     return chunks

# def transcribe_audio_file(filename):
#     """Transcribe audio file, splitting if necessary"""
    
#     # Check file size (Groq has a 25MB limit)
#     file_size = os.path.getsize(filename)
#     max_size = 25 * 1024 * 1024  # 25MB in bytes
    
#     if file_size <= max_size:
#         # File is small enough, transcribe directly
#         with open(filename, "rb") as file:
#             transcription = client.audio.transcriptions.create(
#                 file=file,
#                 model="distil-whisper-large-v3-en",  # Changed to match your rate limits table
#                 prompt="Specify context or spelling",
#                 response_format="verbose_json",
#                 timestamp_granularities=["word", "segment"],
#                 language="en",
#                 temperature=0.0
#             )
#             return transcription
#     else:
#         # File is too large, split it
#         print(f"File size ({file_size / (1024*1024):.1f}MB) exceeds limit. Splitting audio...")
        
#         chunks = split_audio(filename)
#         all_transcriptions = []
        
#         for i, chunk in enumerate(chunks):
#             # Save chunk to temporary file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#                 chunk.export(temp_file.name, format="wav")
                
#                 # Transcribe chunk
#                 with open(temp_file.name, "rb") as file:
#                     transcription = client.audio.transcriptions.create(
#                         file=file,
#                         model="distil-whisper-large-v3-en",  # Changed to match your rate limits table
#                         prompt="Specify context or spelling",
#                         response_format="verbose_json",
#                         timestamp_granularities=["word", "segment"],
#                         language="en",
#                         temperature=0.0
#                     )
#                     all_transcriptions.append(transcription)
#                     print(f"Processed chunk {i+1}/{len(chunks)}")
                
#                 # Clean up temporary file
#                 os.unlink(temp_file.name)
        
#         return combine_transcriptions(all_transcriptions)

# def combine_transcriptions(transcriptions):
#     """Combine multiple transcription objects into one"""
#     if len(transcriptions) == 1:
#         return transcriptions[0]
    
#     # Combine all text
#     combined_text = " ".join([t.text for t in transcriptions])
    
#     # For simplicity, return the first transcription with combined text
#     # In a real application, you'd want to properly merge timestamps
#     result = transcriptions[0]
#     result.text = combined_text
    
#     return result


# import glob

# filenames = glob.glob("./MilestonesGeneration/Videos/*.wav")

# filename = glob.glob("./MilestonesGeneration/Videos/*.wav")[0]

# try:
#     # Transcribe the audio file
#     transcription = transcribe_audio_file(filename)
    
#     # Print the transcription
#     print(json.dumps(transcription, indent=2, default=str))
    
# except Exception as e:
#     print(f"Error during transcription: {e}")
    
#     # Alternative: Use a smaller model or different settings
#     print("Trying with basic transcription...")
#     try:
#         with open(filename, "rb") as file:
#             transcription = client.audio.transcriptions.create(
#                 file=file,
#                 model="distil-whisper-large-v3-en",
#                 response_format="text"  # Simpler format
#             )
#             print("Transcription text:", transcription)
#     except Exception as e2:
#         print(f"Alternative method also failed: {e2}")
#         print("Consider reducing audio file size or quality before upload.")

# import os
# import json
# from groq import Groq
# from pydub import AudioSegment
# import tempfile

# # Initialize the Groq client
# client = Groq(
#     api_key=secret_value_0
# )

# def split_audio(file_path, chunk_length_ms=100000):  
#     """Split audio file into smaller chunks"""
#     audio = AudioSegment.from_file(file_path)
#     chunks = []
    
#     for i in range(0, len(audio), chunk_length_ms):
#         chunk = audio[i:i + chunk_length_ms]
#         chunks.append(chunk)
    
#     return chunks

# def transcribe_audio_file(filename):
#     """Transcribe audio file, splitting if necessary"""
    
#     # Check file size (Groq has a 25MB limit)
#     file_size = os.path.getsize(filename)
#     max_size = 25 * 1024 * 1024  # 25MB in bytes
    
#     if file_size <= max_size:
#         # File is small enough, transcribe directly
#         with open(filename, "rb") as file:
#             transcription = client.audio.transcriptions.create(
#                 file=file,
#                 model="distil-whisper-large-v3-en",  # Changed to match your rate limits table
#                 prompt="Specify context or spelling",
#                 response_format="verbose_json",
#                 timestamp_granularities=["word", "segment"],
#                 language="en",
#                 temperature=0.0
#             )
#             return transcription
#     else:
#         # File is too large, split it
#         print(f"File size ({file_size / (1024*1024):.1f}MB) exceeds limit. Splitting audio...")
        
#         chunks = split_audio(filename)
#         all_transcriptions = []
        
#         for i, chunk in enumerate(chunks):
#             # Save chunk to temporary file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#                 chunk.export(temp_file.name, format="wav")
                
#                 # Transcribe chunk
#                 with open(temp_file.name, "rb") as file:
#                     transcription = client.audio.transcriptions.create(
#                         file=file,
#                         model="distil-whisper-large-v3-en",  # Changed to match your rate limits table
#                         prompt="Specify context or spelling",
#                         response_format="verbose_json",
#                         timestamp_granularities=["word", "segment"],
#                         language="en",
#                         temperature=0.0
#                     )
#                     all_transcriptions.append(transcription)
#                     print(f"Processed chunk {i+1}/{len(chunks)}")
                
#                 # Clean up temporary file
#                 os.unlink(temp_file.name)
        
#         return combine_transcriptions(all_transcriptions)

# def combine_transcriptions(transcriptions):
#     """Combine multiple transcription objects into one"""
#     if len(transcriptions) == 1:
#         return transcriptions[0]
    
#     # Combine all text
#     combined_text = " ".join([t.text for t in transcriptions])
    
#     # For simplicity, return the first transcription with combined text
#     # In a real application, you'd want to properly merge timestamps
#     result = transcriptions[0]
#     result.text = combined_text
    
#     return result


# import glob

# filenames = glob.glob("./MilestonesGeneration/Videos/*.wav")

# filename = glob.glob("./MilestonesGeneration/Videos/*.wav")[0]

# try:
#     # Transcribe the audio file
#     transcription = transcribe_audio_file(filename)
    
#     # Print the transcription
#     print(json.dumps(transcription, indent=2, default=str))
    
# except Exception as e:
#     print(f"Error during transcription: {e}")
    
#     # Alternative: Use a smaller model or different settings
#     print("Trying with basic transcription...")
#     try:
#         with open(filename, "rb") as file:
#             transcription = client.audio.transcriptions.create(
#                 file=file,
#                 model="distil-whisper-large-v3-en",
#                 response_format="text"  # Simpler format
#             )
#             print("Transcription text:", transcription)
#     except Exception as e2:
#         print(f"Alternative method also failed: {e2}")
#         print("Consider reducing audio file size or quality before upload.")

