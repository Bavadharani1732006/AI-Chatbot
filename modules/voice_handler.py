import speech_recognition as sr
import pyttsx3
import os
from threading import Thread

class VoiceHandler:
    """Handle voice input and output for chatbot"""
    
    def __init__(self, rate=150):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', 0.9)
        self.is_speaking = False
    
    def speech_to_text(self):
        """Convert speech to text using microphone"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=10)
            
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                return "Sorry, I didn't understand that. Could you please repeat?"
            except sr.RequestError as e:
                return f"Error with speech recognition service: {e}"
        
        except Exception as e:
            print(f"Error accessing microphone: {e}")
            return "Error: Microphone not available"
    
    def text_to_speech(self, text, use_thread=True):
        """Convert text to speech"""
        try:
            if use_thread:
                thread = Thread(target=self._speak, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self._speak(text)
        except Exception as e:
            print(f"Error in text to speech: {e}")
    
    def _speak(self, text):
        """Internal method to speak text"""
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error speaking: {e}")
            self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            self.engine.stop()
            self.is_speaking = False
        except Exception as e:
            print(f"Error stopping speech: {e}")
    
    def set_rate(self, rate):
        """Set speech rate"""
        try:
            self.engine.setProperty('rate', rate)
        except Exception as e:
            print(f"Error setting rate: {e}")
    
    def set_voice_type(self, voice_id=0):
        """Set voice type (male/female)"""
        try:
            voices = self.engine.getProperty('voices')
            if voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
        except Exception as e:
            print(f"Error setting voice: {e}")
    
    def get_available_voices(self):
        """Get list of available voices"""
        try:
            voices = self.engine.getProperty('voices')
            return [{'id': voice.id, 'name': voice.name} for voice in voices]
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []

# Initialize voice handler
voice_handler = VoiceHandler()
