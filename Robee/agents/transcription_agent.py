"""
Transcription Agent - Handles audio/video transcription and speech processing
"""
import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

@dataclass
class TranscriptionSegment:
    """Individual transcription segment"""
    start_time: float
    end_time: float
    text: str
    confidence: float
    speaker: Optional[str] = None
    language: Optional[str] = None

@dataclass
class TranscriptionResult:
    """Complete transcription result"""
    segments: List[TranscriptionSegment]
    full_text: str
    duration: float
    language: str
    confidence: float
    word_count: int
    speaker_count: int
    speakers: List[str]

@dataclass
class SpeakerSegment:
    """Speaker diarization segment"""
    speaker_id: str
    start_time: float
    end_time: float
    confidence: float

class TranscriptionAgent:
    """
    Primary Responsibilities:
    - Transcribe audio and video content
    - Perform speaker diarization
    - Process real-time speech streams
    - Handle multiple languages and accents
    - Clean and format transcription output
    """
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.speech_recognizer = SpeechRecognizer()
        self.speaker_identifier = SpeakerIdentifier()
        self.text_formatter = TranscriptionFormatter()
        
        # Transcription settings
        self.supported_formats = ['.wav', '.mp3', '.mp4', '.m4a', '.flac', '.aac']
        self.default_language = 'en-US'
        self.confidence_threshold = 0.7
        
        # Processing options
        self.enable_speaker_diarization = True
        self.enable_punctuation = True
        self.enable_formatting = True
        self.chunk_duration = 30  # seconds per processing chunk
        
        # Cache for processed audio
        self.transcription_cache = {}
        
    def transcribe_audio_file(self, file_path: str, options: Dict[str, Any] = None) -> TranscriptionResult:
        """Transcribe audio file"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Validate file format
        if not self._is_supported_format(file_path):
            raise ValueError(f"Unsupported audio format. Supported: {self.supported_formats}")
        
        # Check cache
        file_hash = self._get_file_hash(file_path)
        if file_hash in self.transcription_cache:
            return self.transcription_cache[file_hash]
        
        # Set up options
        transcription_options = self._prepare_transcription_options(options)
        
        # Process audio file
        audio_info = self.audio_processor.analyze_audio(file_path)
        
        # Chunk audio for processing
        chunks = self.audio_processor.chunk_audio(file_path, self.chunk_duration)
        
        # Transcribe each chunk
        all_segments = []
        current_time_offset = 0.0
        
        for i, chunk_path in enumerate(chunks):
            try:
                chunk_segments = self._transcribe_chunk(
                    chunk_path, 
                    current_time_offset, 
                    transcription_options
                )
                all_segments.extend(chunk_segments)
                current_time_offset += self.chunk_duration
                
                # Clean up temporary chunk file
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
                    
            except Exception as e:
                print(f"Error transcribing chunk {i}: {e}")
                continue
        
        # Perform speaker diarization if enabled
        if transcription_options.get('enable_speaker_diarization', True):
            all_segments = self.speaker_identifier.identify_speakers(all_segments, file_path)
        
        # Create final result
        result = self._create_transcription_result(all_segments, audio_info, transcription_options)
        
        # Apply post-processing
        result = self.text_formatter.format_transcription(result)
        
        # Cache result
        self.transcription_cache[file_hash] = result
        
        return result
        
    def transcribe_real_time_stream(self, audio_stream, callback_function: callable = None) -> List[TranscriptionSegment]:
        """Transcribe real-time audio stream"""
        
        segments = []
        buffer = []
        
        try:
            for audio_chunk in audio_stream:
                buffer.append(audio_chunk)
                
                # Process when buffer reaches threshold
                if len(buffer) >= 10:  # Process every 10 chunks
                    segment = self._process_real_time_chunk(buffer)
                    if segment:
                        segments.append(segment)
                        
                        # Call callback if provided
                        if callback_function:
                            callback_function(segment)
                    
                    buffer = []
                    
        except Exception as e:
            print(f"Error in real-time transcription: {e}")
        
        return segments
        
    def transcribe_meeting(self, audio_file: str, participant_names: List[str] = None) -> Dict[str, Any]:
        """Transcribe meeting with speaker identification"""
        
        # Transcribe with speaker diarization
        transcription = self.transcribe_audio_file(audio_file, {
            'enable_speaker_diarization': True,
            'enable_punctuation': True,
            'meeting_mode': True
        })
        
        # Format for meeting context
        meeting_transcript = self._format_meeting_transcript(transcription, participant_names)
        
        # Extract meeting insights
        insights = self._extract_meeting_insights(transcription)
        
        return {
            'transcript': meeting_transcript,
            'insights': insights,
            'duration': transcription.duration,
            'speakers': transcription.speakers,
            'word_count': transcription.word_count
        }
        
    def convert_audio_format(self, input_file: str, output_format: str = 'wav') -> str:
        """Convert audio to supported format"""
        
        return self.audio_processor.convert_format(input_file, output_format)
        
    def enhance_audio_quality(self, audio_file: str) -> str:
        """Enhance audio quality for better transcription"""
        
        return self.audio_processor.enhance_audio(audio_file)
        
    def extract_audio_from_video(self, video_file: str) -> str:
        """Extract audio track from video file"""
        
        return self.audio_processor.extract_audio_from_video(video_file)
        
    def get_transcription_languages(self) -> List[Dict[str, str]]:
        """Get list of supported transcription languages"""
        
        return [
            {'code': 'en-US', 'name': 'English (US)'},
            {'code': 'en-GB', 'name': 'English (UK)'},
            {'code': 'es-ES', 'name': 'Spanish'},
            {'code': 'fr-FR', 'name': 'French'},
            {'code': 'de-DE', 'name': 'German'},
            {'code': 'it-IT', 'name': 'Italian'},
            {'code': 'pt-PT', 'name': 'Portuguese'},
            {'code': 'ja-JP', 'name': 'Japanese'},
            {'code': 'ko-KR', 'name': 'Korean'},
            {'code': 'zh-CN', 'name': 'Chinese (Simplified)'}
        ]
        
    def validate_transcription_quality(self, result: TranscriptionResult) -> Dict[str, Any]:
        """Validate transcription quality"""
        
        quality_metrics = {
            'overall_confidence': result.confidence,
            'segments_count': len(result.segments),
            'low_confidence_segments': 0,
            'silence_gaps': 0,
            'speaker_changes': 0,
            'quality_score': 0.0
        }
        
        # Analyze segments
        for i, segment in enumerate(result.segments):
            if segment.confidence < self.confidence_threshold:
                quality_metrics['low_confidence_segments'] += 1
                
            # Check for speaker changes
            if i > 0 and result.segments[i-1].speaker != segment.speaker:
                quality_metrics['speaker_changes'] += 1
                
            # Check for silence gaps
            if i > 0:
                gap = segment.start_time - result.segments[i-1].end_time
                if gap > 2.0:  # More than 2 seconds
                    quality_metrics['silence_gaps'] += 1
        
        # Calculate quality score
        confidence_score = result.confidence
        completeness_score = 1.0 - (quality_metrics['silence_gaps'] / max(len(result.segments), 1))
        consistency_score = 1.0 - (quality_metrics['low_confidence_segments'] / max(len(result.segments), 1))
        
        quality_metrics['quality_score'] = (confidence_score + completeness_score + consistency_score) / 3
        
        return quality_metrics
        
    def _is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.supported_formats
        
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file caching"""
        
        file_stat = os.stat(file_path)
        return f"{file_path}_{file_stat.st_size}_{file_stat.st_mtime}"
        
    def _prepare_transcription_options(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare transcription options with defaults"""
        
        default_options = {
            'language': self.default_language,
            'enable_speaker_diarization': self.enable_speaker_diarization,
            'enable_punctuation': self.enable_punctuation,
            'enable_formatting': self.enable_formatting,
            'confidence_threshold': self.confidence_threshold,
            'meeting_mode': False
        }
        
        if options:
            default_options.update(options)
            
        return default_options
        
    def _transcribe_chunk(self, chunk_path: str, time_offset: float, 
                         options: Dict[str, Any]) -> List[TranscriptionSegment]:
        """Transcribe individual audio chunk"""
        
        # This would integrate with actual speech recognition service
        # For now, return simulated segments
        segments = []
        
        try:
            # Simulate transcription processing
            raw_transcription = self.speech_recognizer.transcribe(chunk_path, options)
            
            # Parse raw transcription into segments
            segments = self._parse_raw_transcription(raw_transcription, time_offset)
            
        except Exception as e:
            print(f"Error transcribing chunk: {e}")
            # Return empty segment to maintain timeline
            segments = [TranscriptionSegment(
                start_time=time_offset,
                end_time=time_offset + self.chunk_duration,
                text="[Transcription Error]",
                confidence=0.0
            )]
        
        return segments
        
    def _parse_raw_transcription(self, raw_data: Dict[str, Any], time_offset: float) -> List[TranscriptionSegment]:
        """Parse raw transcription data into segments"""
        
        segments = []
        
        # Example parsing (would depend on actual service format)
        if 'results' in raw_data:
            for result in raw_data['results']:
                if 'alternatives' in result and result['alternatives']:
                    alternative = result['alternatives'][0]
                    
                    segment = TranscriptionSegment(
                        start_time=time_offset + result.get('start_time', 0.0),
                        end_time=time_offset + result.get('end_time', self.chunk_duration),
                        text=alternative.get('transcript', ''),
                        confidence=alternative.get('confidence', 0.5)
                    )
                    segments.append(segment)
        
        return segments
        
    def _create_transcription_result(self, segments: List[TranscriptionSegment], 
                                   audio_info: Dict[str, Any], 
                                   options: Dict[str, Any]) -> TranscriptionResult:
        """Create final transcription result"""
        
        # Combine all text
        full_text = ' '.join([segment.text for segment in segments if segment.text])
        
        # Calculate overall confidence
        if segments:
            total_confidence = sum(segment.confidence for segment in segments)
            avg_confidence = total_confidence / len(segments)
        else:
            avg_confidence = 0.0
        
        # Get unique speakers
        speakers = list(set([segment.speaker for segment in segments if segment.speaker]))
        
        return TranscriptionResult(
            segments=segments,
            full_text=full_text,
            duration=audio_info.get('duration', 0.0),
            language=options.get('language', self.default_language),
            confidence=avg_confidence,
            word_count=len(full_text.split()),
            speaker_count=len(speakers),
            speakers=speakers
        )
        
    def _process_real_time_chunk(self, audio_buffer: List) -> Optional[TranscriptionSegment]:
        """Process real-time audio chunk"""
        
        try:
            # Combine audio buffer
            combined_audio = self.audio_processor.combine_audio_chunks(audio_buffer)
            
            # Quick transcription
            result = self.speech_recognizer.transcribe_quick(combined_audio)
            
            if result and result.get('text'):
                return TranscriptionSegment(
                    start_time=time.time(),
                    end_time=time.time() + 1.0,
                    text=result['text'],
                    confidence=result.get('confidence', 0.5)
                )
                
        except Exception as e:
            print(f"Error processing real-time chunk: {e}")
            
        return None
        
    def _format_meeting_transcript(self, transcription: TranscriptionResult, 
                                 participant_names: List[str] = None) -> str:
        """Format transcription for meeting context"""
        
        formatted_lines = []
        current_speaker = None
        
        for segment in transcription.segments:
            # Determine speaker name
            speaker_name = segment.speaker
            if participant_names and segment.speaker:
                try:
                    speaker_index = int(segment.speaker.replace('Speaker_', ''))
                    if speaker_index < len(participant_names):
                        speaker_name = participant_names[speaker_index]
                except:
                    pass
            
            # Format timestamp
            timestamp = self._format_timestamp(segment.start_time)
            
            # Add speaker change
            if current_speaker != speaker_name:
                formatted_lines.append(f"\n[{timestamp}] {speaker_name}:")
                current_speaker = speaker_name
            
            # Add text
            formatted_lines.append(f"{segment.text}")
        
        return '\n'.join(formatted_lines)
        
    def _extract_meeting_insights(self, transcription: TranscriptionResult) -> Dict[str, Any]:
        """Extract insights from meeting transcription"""
        
        insights = {
            'speaking_time': {},
            'key_topics': [],
            'action_items': [],
            'decisions': [],
            'questions': []
        }
        
        # Calculate speaking time per speaker
        for speaker in transcription.speakers:
            speaker_segments = [s for s in transcription.segments if s.speaker == speaker]
            total_time = sum(s.end_time - s.start_time for s in speaker_segments)
            insights['speaking_time'][speaker] = round(total_time, 2)
        
        # Extract content insights
        full_text = transcription.full_text.lower()
        
        # Simple keyword extraction for topics
        topic_keywords = ['project', 'budget', 'timeline', 'deadline', 'requirement', 'goal']
        for keyword in topic_keywords:
            if keyword in full_text:
                insights['key_topics'].append(keyword)
        
        # Extract action items (simple pattern matching)
        action_patterns = [r'will (.*?)(?:\.|$)', r'should (.*?)(?:\.|$)', r'need to (.*?)(?:\.|$)']
        for pattern in action_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            insights['action_items'].extend(matches[:5])  # Limit to 5
        
        # Extract decisions
        decision_patterns = [r'decided (.*?)(?:\.|$)', r'agreed (.*?)(?:\.|$)']
        for pattern in decision_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            insights['decisions'].extend(matches[:5])
        
        # Extract questions
        question_pattern = r'([^\.]*\?)'
        questions = re.findall(question_pattern, transcription.full_text)
        insights['questions'] = questions[:10]  # Limit to 10
        
        return insights
        
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as timestamp"""
        
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


class AudioProcessor:
    """Handles audio file processing"""
    
    def analyze_audio(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio file properties"""
        
        # This would use actual audio processing library
        # For now, return simulated analysis
        return {
            'duration': 300.0,  # 5 minutes
            'sample_rate': 44100,
            'channels': 2,
            'bit_depth': 16,
            'format': 'wav'
        }
        
    def chunk_audio(self, file_path: str, chunk_duration: float) -> List[str]:
        """Split audio into chunks for processing"""
        
        # This would use actual audio processing
        # For now, return simulated chunk paths
        chunks = []
        audio_info = self.analyze_audio(file_path)
        duration = audio_info['duration']
        
        num_chunks = int(duration / chunk_duration) + 1
        
        for i in range(num_chunks):
            chunk_path = f"temp_chunk_{i}.wav"
            chunks.append(chunk_path)
            
            # In real implementation, would create actual audio chunks
            # For now, just create placeholder files
            with open(chunk_path, 'w') as f:
                f.write(f"Audio chunk {i}")
        
        return chunks
        
    def convert_format(self, input_file: str, output_format: str) -> str:
        """Convert audio format"""
        
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format}"
        
        # This would use actual audio conversion
        # For now, just copy file
        if input_file != output_file:
            with open(input_file, 'rb') as src, open(output_file, 'wb') as dst:
                dst.write(src.read())
        
        return output_file
        
    def enhance_audio(self, audio_file: str) -> str:
        """Enhance audio quality"""
        
        enhanced_file = f"{os.path.splitext(audio_file)[0]}_enhanced.wav"
        
        # This would apply actual audio enhancement
        # For now, just copy file
        with open(audio_file, 'rb') as src, open(enhanced_file, 'wb') as dst:
            dst.write(src.read())
        
        return enhanced_file
        
    def extract_audio_from_video(self, video_file: str) -> str:
        """Extract audio from video"""
        
        audio_file = f"{os.path.splitext(video_file)[0]}_audio.wav"
        
        # This would use actual video processing
        # For now, create placeholder audio file
        with open(audio_file, 'w') as f:
            f.write("Extracted audio")
        
        return audio_file
        
    def combine_audio_chunks(self, chunks: List) -> bytes:
        """Combine audio chunks"""
        
        # This would combine actual audio data
        # For now, return placeholder
        return b"combined_audio_data"


class SpeechRecognizer:
    """Handles speech recognition"""
    
    def transcribe(self, audio_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio file"""
        
        # This would integrate with actual speech recognition service
        # (Google Speech-to-Text, Azure, AWS, etc.)
        
        # Simulated transcription result
        return {
            'results': [
                {
                    'start_time': 0.0,
                    'end_time': 10.0,
                    'alternatives': [
                        {
                            'transcript': 'Hello, this is a sample transcription.',
                            'confidence': 0.95
                        }
                    ]
                },
                {
                    'start_time': 10.0,
                    'end_time': 20.0,
                    'alternatives': [
                        {
                            'transcript': 'This is another segment of the audio.',
                            'confidence': 0.87
                        }
                    ]
                }
            ]
        }
        
    def transcribe_quick(self, audio_data: bytes) -> Dict[str, Any]:
        """Quick transcription for real-time processing"""
        
        # This would do quick speech recognition
        return {
            'text': 'Real-time transcription text',
            'confidence': 0.8
        }


class SpeakerIdentifier:
    """Handles speaker diarization and identification"""
    
    def identify_speakers(self, segments: List[TranscriptionSegment], 
                         audio_file: str) -> List[TranscriptionSegment]:
        """Identify speakers in transcription segments"""
        
        # This would use actual speaker diarization
        # For now, assign speakers based on simple rules
        
        current_speaker = "Speaker_1"
        speaker_change_threshold = 5.0  # Change speaker every 5 seconds
        
        for i, segment in enumerate(segments):
            # Simple speaker assignment
            if i > 0 and segment.start_time - segments[i-1].start_time > speaker_change_threshold:
                current_speaker = "Speaker_2" if current_speaker == "Speaker_1" else "Speaker_1"
            
            segment.speaker = current_speaker
        
        return segments
        
    def train_speaker_model(self, speaker_name: str, audio_samples: List[str]) -> bool:
        """Train speaker identification model"""
        
        # This would train actual speaker recognition model
        print(f"Training speaker model for {speaker_name} with {len(audio_samples)} samples")
        return True
        
    def identify_known_speakers(self, segments: List[TranscriptionSegment]) -> List[TranscriptionSegment]:
        """Identify known speakers from trained models"""
        
        # This would use trained models to identify speakers
        # For now, just assign generic speaker names
        for segment in segments:
            if not segment.speaker:
                segment.speaker = "Unknown_Speaker"
        
        return segments


class TranscriptionFormatter:
    """Formats and cleans transcription output"""
    
    def format_transcription(self, result: TranscriptionResult) -> TranscriptionResult:
        """Format transcription with proper punctuation and structure"""
        
        # Apply formatting to each segment
        formatted_segments = []
        
        for segment in result.segments:
            formatted_text = self._format_segment_text(segment.text)
            
            formatted_segment = TranscriptionSegment(
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=formatted_text,
                confidence=segment.confidence,
                speaker=segment.speaker,
                language=segment.language
            )
            formatted_segments.append(formatted_segment)
        
        # Update full text
        formatted_full_text = ' '.join([seg.text for seg in formatted_segments])
        
        # Create new result with formatted content
        formatted_result = TranscriptionResult(
            segments=formatted_segments,
            full_text=formatted_full_text,
            duration=result.duration,
            language=result.language,
            confidence=result.confidence,
            word_count=len(formatted_full_text.split()),
            speaker_count=result.speaker_count,
            speakers=result.speakers
        )
        
        return formatted_result
        
    def _format_segment_text(self, text: str) -> str:
        """Format individual segment text"""
        
        if not text:
            return text
        
        # Basic text cleaning
        formatted = text.strip()
        
        # Fix capitalization
        formatted = self._fix_capitalization(formatted)
        
        # Add punctuation
        formatted = self._add_punctuation(formatted)
        
        # Remove filler words (optional)
        formatted = self._remove_filler_words(formatted)
        
        # Fix common transcription errors
        formatted = self._fix_common_errors(formatted)
        
        return formatted
        
    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization in text"""
        
        if not text:
            return text
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Capitalize after periods
        text = re.sub(r'\.(\s+)([a-z])', lambda m: '.' + m.group(1) + m.group(2).upper(), text)
        
        # Capitalize "I"
        text = re.sub(r'\bi\b', 'I', text)
        
        return text
        
    def _add_punctuation(self, text: str) -> str:
        """Add basic punctuation"""
        
        if not text:
            return text
        
        # Add period at end if missing
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Add question marks for questions
        question_words = ['what', 'where', 'when', 'why', 'how', 'who', 'which']
        words = text.lower().split()
        
        if words and words[0] in question_words:
            text = text.rstrip('.') + '?'
        
        return text
        
    def _remove_filler_words(self, text: str) -> str:
        """Remove filler words (optional)"""
        
        filler_words = ['um', 'uh', 'ah', 'er', 'like', 'you know']
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in filler_words]
        
        return ' '.join(filtered_words)
        
    def _fix_common_errors(self, text: str) -> str:
        """Fix common transcription errors"""
        
        # Common misrecognitions
        corrections = {
            'there are': 'there are',
            'their are': 'there are',
            'they\'re are': 'there are',
            'to be': 'to be',
            'too be': 'to be',
            'two be': 'to be'
        }
        
        for incorrect, correct in corrections.items():
            text = re.sub(re.escape(incorrect), correct, text, flags=re.IGNORECASE)
        
        return text


# Utility functions for backward compatibility
def transcribe_audio(file_path: str, language: str = 'en-US') -> str:
    """Simple transcription function for backward compatibility"""
    
    agent = TranscriptionAgent()
    result = agent.transcribe_audio_file(file_path, {'language': language})
    
    return result.full_text


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video for backward compatibility"""
    
    agent = TranscriptionAgent()
    return agent.extract_audio_from_video(video_path)


def transcribe_meeting_audio(audio_path: str, participants: List[str] = None) -> Dict[str, Any]:
    """Transcribe meeting audio for backward compatibility"""
    
    agent = TranscriptionAgent()
    return agent.transcribe_meeting(audio_path, participants)
