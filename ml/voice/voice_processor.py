import os
import tempfile
import speech_recognition as sr
from gtts import gTTS
import streamlit as st
from pathlib import Path
import whisper
import numpy as np
import soundfile as sf

class VoiceProcessor:
    def __init__(self):
        """Initialize voice processing components."""
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model("base")
        
    def transcribe_audio(self, audio_data, sample_rate, use_whisper=True):
        """
        Transcribe audio data to text using either Whisper or SpeechRecognition.
        
        Args:
            audio_data (numpy.ndarray): Audio data as numpy array
            sample_rate (int): Sample rate of the audio
            use_whisper (bool): Whether to use Whisper (True) or SpeechRecognition (False)
            
        Returns:
            str: Transcribed text
        """
        try:
            if use_whisper:
                # Save audio to temporary file for Whisper
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data, sample_rate)
                    result = self.whisper_model.transcribe(temp_file.name)
                    os.unlink(temp_file.name)
                    return result["text"]
            else:
                # Use SpeechRecognition
                audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            st.error(f"Error in transcription: {str(e)}")
            return None

    def text_to_speech(self, text, output_path=None):
        """
        Convert text to speech using gTTS.
        
        Args:
            text (str): Text to convert to speech
            output_path (str, optional): Path to save the audio file
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            st.error(f"Error in text-to-speech conversion: {str(e)}")
            return None

    def process_audio_input(self, audio_data, sample_rate):
        """
        Process audio input: transcribe and return text.
        
        Args:
            audio_data (numpy.ndarray): Audio data as numpy array
            sample_rate (int): Sample rate of the audio
            
        Returns:
            str: Transcribed text
        """
        return self.transcribe_audio(audio_data, sample_rate)

    def process_text_response(self, text):
        """
        Process text response: convert to speech.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            str: Path to the generated audio file
        """
        return self.text_to_speech(text) 