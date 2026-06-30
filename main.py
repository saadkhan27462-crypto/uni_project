import customtkinter as ctk
import langid
from datetime import datetime 
from deep_translator import GoogleTranslator
import pyttsx3
import threading
import webbrowser
import json
import os
import time

# ---------------- APP SETTINGS ----------------

# History file
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Language Detector Pro")
root.geometry("1200x700")

# Load history from file
history = load_history()

# ---------------- FUNCTIONS ----------------

def show_page(page):
    detect_page.pack_forget()
    history_page.pack_forget()
    about_page.pack_forget()

    if page == "detect":
        detect_page.pack(fill="both", expand=True, padx=20, pady=20)
    elif page == "history":
        history_page.pack(fill="both", expand=True, padx=20, pady=20)
    elif page == "about":
        about_page.pack(fill="both", expand=True, padx=20, pady=20)

def detect_language():
    text = textbox.get("1.0", "end").strip()

    # Better input validation
    if len(text) < 3:
        result_lang.configure(text="⚠️ Enter at least 3 characters")
        confidence_label.configure(text="0%")
        progress.set(0)
        return

    # Check if text contains only numbers/special characters
    if not any(c.isalpha() for c in text):
        result_lang.configure(text="⚠️ Enter text with letters")
        confidence_label.configure(text="0%")
        progress.set(0)
        return

    try:
        lang, confidence = langid.classify(text)

        languages = {
            "en": "English", "ur": "Urdu", "fr": "French",
            "es": "Spanish", "de": "German", "ar": "Arabic",
            "hi": "Hindi", "ru": "Russian", "it": "Italian",
            "pt": "Portuguese", "zh": "Chinese", "ja": "Japanese",
            "ko": "Korean", "nl": "Dutch", "tr": "Turkish"
        }

        language_name = languages.get(lang, lang)
        
        # Better confidence calculation
        confidence_score = min(abs(confidence) * 15, 100)
        confidence_score = max(confidence_score, 10)  # Minimum 10%

        result_lang.configure(text=language_name)
        confidence_label.configure(text=f"{confidence_score:.1f}%")
        progress.set(confidence_score / 100)

        # Save to history with more detail
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"[{current_time}] {language_name} ({confidence_score:.1f}%)"
        history.append(history_entry)
        history_box.insert("end", history_entry + "\n")
        history_box.see("end")  # Auto-scroll
        save_history()
        
    except Exception as e:
        result_lang.configure(text=f"⚠️ Error: {str(e)[:30]}")
        confidence_label.configure(text="0%")
        progress.set(0)

def clear_text():
    textbox.delete("1.0", "end")
    counter.configure(text="Characters: 0")
    result_lang.configure(text="Waiting...")
    confidence_label.configure(text="0%")
    progress.set(0)

def clear_history():
    history_box.delete("1.0", "end")
    history.clear()
    save_history()

def update_counter(event=None):
    chars = len(textbox.get("1.0", "end-1c"))
    counter.configure(text=f"Characters: {chars}")

def translate_text():
    text = textbox.get("1.0", "end").strip()
    
    if len(text) < 1:
        translated_result.configure(text="⚠️ Please enter text to translate", text_color="orange")
        return
    
    # Check if text has letters
    if not any(c.isalpha() for c in text):
        translated_result.configure(text="⚠️ Enter text with letters to translate", text_color="orange")
        return
    
    target_language = language_dropdown.get()
    
    lang_codes = {
        "English": "en", "Urdu": "ur", "French": "fr",
        "Spanish": "es", "German": "de", "Arabic": "ar",
        "Hindi": "hi", "Japanese": "ja", "Korean": "ko",
        "Dutch": "nl", "Turkish": "tr"
    }
    
    target_code = lang_codes.get(target_language, "en")
    
    try:
        translated_result.configure(text="🔄 Translating...", text_color="blue")
        root.update()
        
        translator = GoogleTranslator(source='auto', target=target_code)
        translated = translator.translate(text)
        translated_result.configure(text=translated, text_color="white")
    except Exception as e:
        translated_result.configure(text=f"⚠️ Translation error: {str(e)[:50]}", text_color="red")

def text_to_speech():
    """Improved TTS with fallback options"""
    text = textbox.get("1.0", "end").strip()
    
    if len(text) < 1:
        tts_status.configure(text="⚠️ No text to speak!", text_color="orange")
        return
    
    # Try TTS first
    if TTS_AVAILABLE and tts_engine:
        try:
            tts_status.configure(text="🔊 Speaking...", text_color="green")
            
            def speak():
                try:
                    # Stop any ongoing speech
                    try:
                        tts_engine.stop()
                    except:
                        pass
                    
                    tts_engine.say(text)
                    tts_engine.runAndWait()
                    root.after(0, lambda: tts_status.configure(text="✅ Done!", text_color="green"))
                except Exception as e:
                    root.after(0, lambda: tts_status.configure(text=f"⚠️ TTS failed: {str(e)[:30]}", text_color="red"))
                    # Fallback to web TTS
                    root.after(0, web_tts_fallback)
            
            threading.Thread(target=speak, daemon=True).start()
            return
            
        except Exception as e:
            tts_status.configure(text=f"⚠️ TTS error, using web fallback", text_color="orange")
            web_tts_fallback()
    else:
        # Use web-based TTS
        web_tts_fallback()

def web_tts_fallback():
    """Use web-based TTS as fallback"""
    text = textbox.get("1.0", "end").strip()
    if len(text) < 1:
        return
    
    # Use Google's TTS web service
    encoded_text = text.replace(' ', '%20')
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=en&client=tw-ob"
    
    tts_status.configure(text="🌐 Opening web TTS...", text_color="blue")
    webbrowser.open(url)
    
    # Show instructions
    dialog = ctk.CTkToplevel(root)
    dialog.title("🔊 Web TTS")
    dialog.geometry("500x300")
    
    instructions = """
    🌐 **Web TTS Fallback**
    
    Audio should play automatically.
    If not:
    1. Click the play button on the page
    2. Or download and play the audio file
    
    This is a fallback when local TTS fails.
    """
    
    label = ctk.CTkLabel(
        dialog,
        text=instructions,
        justify="left",
        font=("Arial", 14)
    )
    label.pack(padx=20, pady=20)
    
    ctk.CTkButton(
        dialog,
        text="✓ Close",
        command=dialog.destroy
    ).pack(pady=10)

def stop_speech():
    """Stop TTS speech"""
    try:
        if tts_engine:
            tts_engine.stop()
        tts_status.configure(text="⏹️ Stopped", text_color="orange")
    except:
        pass

def speech_to_text_browser():
    """Use browser-based speech recognition (no PyAudio needed)"""
    stt_status.configure(text="🌐 Opening speech recognition...", text_color="blue")
    
    # Open multiple options for STT
    webbrowser.open("https://dictation.io/speech")
    
    # Show instructions with more options
    dialog = ctk.CTkToplevel(root)
    dialog.title("🎤 Speech-to-Text Options")
    dialog.geometry("600x500")
    
    instructions = """
    🌐 **Speech-to-Text Options**
    
    **Option 1: Dictation.io (Recommended)**
    1. Browser will open Dictation.io
    2. Click "Start Dictation"
    3. Allow microphone access
    4. Speak clearly
    5. Copy and paste text into app
    
    **Option 2: Google Docs**
    1. Open Google Docs in Chrome
    2. Tools → Voice Typing
    3. Click microphone and speak
    
    **Option 3: Mobile**
    • Use phone's voice typing
    • Email or share the text
    • Copy to your computer
    
    **Tips for better accuracy:**
    • Speak clearly and slowly
    • Use a good microphone
    • Minimize background noise
    • Speak in short phrases
    """
    
    label = ctk.CTkLabel(
        dialog,
        text=instructions,
        justify="left",
        font=("Arial", 13)
    )
    label.pack(padx=20, pady=20)
    
    # Add additional STT options buttons
    button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    button_frame.pack(pady=10)
    
    ctk.CTkButton(
        button_frame,
        text="📝 Open Dictation.io",
        command=lambda: [webbrowser.open("https://dictation.io/speech"), dialog.destroy()]
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        button_frame,
        text="📄 Open Google Docs",
        command=lambda: [webbrowser.open("https://docs.google.com/document/create"), dialog.destroy()]
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        dialog,
        text="✓ I understand - Close",
        command=dialog.destroy
    ).pack(pady=10)

# ---------------- SIDEBAR ----------------

sidebar = ctk.CTkFrame(root, width=220, corner_radius=0)
sidebar.pack(side="left", fill="y")

logo = ctk.CTkLabel(sidebar, text="🌍\nLanguage\nDetector", font=("Arial", 28, "bold"))
logo.pack(pady=40)

ctk.CTkButton(sidebar, text="Detect Language", width=180, height=45, 
              command=lambda: show_page("detect")).pack(pady=10)
ctk.CTkButton(sidebar, text="History", width=180, height=45, 
              command=lambda: show_page("history")).pack(pady=10)
ctk.CTkButton(sidebar, text="About", width=180, height=45, 
              command=lambda: show_page("about")).pack(pady=10)

# ---------------- PAGES ----------------

detect_page = ctk.CTkFrame(root, fg_color="transparent")
history_page = ctk.CTkFrame(root, fg_color="transparent")
about_page = ctk.CTkFrame(root, fg_color="transparent")

# ---------------- DETECT PAGE ----------------

title = ctk.CTkLabel(detect_page, text="Detect Language", font=("Arial", 34, "bold"))
title.pack(anchor="w")

subtitle = ctk.CTkLabel(detect_page, text="Enter text below and detect the language", font=("Arial", 16))
subtitle.pack(anchor="w", pady=(0, 15))

text_input_frame = ctk.CTkFrame(detect_page, fg_color="transparent")
text_input_frame.pack(fill="x")

textbox = ctk.CTkTextbox(text_input_frame, height=180, font=("Arial", 16))
textbox.pack(fill="x")
textbox.bind("<KeyRelease>", update_counter)

counter = ctk.CTkLabel(text_input_frame, text="Characters: 0")
counter.pack(anchor="e", pady=5)

# Speech-to-Text Status
stt_status = ctk.CTkLabel(
    text_input_frame,
    text="🎤 Click 'Start Speaking' for web-based voice input",
    font=("Arial", 14)
)
stt_status.pack(anchor="w", pady=(0, 5))

button_frame = ctk.CTkFrame(detect_page, fg_color="transparent")
button_frame.pack(fill="x", pady=10)

# Main buttons
ctk.CTkButton(button_frame, text="🔍 Detect", width=140, height=45, 
              command=detect_language).pack(side="left", padx=5)
ctk.CTkButton(button_frame, text="🗑 Clear", width=140, height=45, 
              command=clear_text).pack(side="left", padx=5)

# --- TTS Controls ---
tts_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
tts_frame.pack(side="left", padx=20)

ctk.CTkLabel(tts_frame, text="Text-to-Speech:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
ctk.CTkButton(tts_frame, text="🔊 Speak", width=120, height=40, 
              command=text_to_speech).pack(side="left", padx=2)
ctk.CTkButton(tts_frame, text="⏹ Stop", width=100, height=40, 
              fg_color="orange", hover_color="darkorange",
              command=stop_speech).pack(side="left", padx=2)

# --- STT Controls ---
stt_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
stt_frame.pack(side="left", padx=20)

ctk.CTkLabel(stt_frame, text="Speech-to-Text:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
ctk.CTkButton(stt_frame, text="🎤 Start Speaking", width=160, height=40,
              fg_color="#2196F3", hover_color="#1976D2",
              command=speech_to_text_browser).pack(side="left", padx=2)

# TTS Status - MOVED HERE BEFORE TTS INITIALIZATION
tts_status = ctk.CTkLabel(detect_page, text="⏳ Initializing TTS...", font=("Arial", 14))
tts_status.pack(anchor="w", pady=(10, 0))

# ---------------- RESULT CARD ----------------

result_card = ctk.CTkFrame(detect_page, height=140)
result_card.pack(fill="x", pady=20)

ctk.CTkLabel(result_card, text="Detected Language", font=("Arial", 16)).pack(pady=(15, 0))
result_lang = ctk.CTkLabel(result_card, text="Waiting...", font=("Arial", 34, "bold"))
result_lang.pack()
confidence_label = ctk.CTkLabel(result_card, text="0%", font=("Arial", 22))
confidence_label.pack()

progress = ctk.CTkProgressBar(result_card, width=500)
progress.pack(pady=10)
progress.set(0)

# ---------------- TRANSLATE SECTION ----------------

translate_frame = ctk.CTkFrame(detect_page, fg_color="transparent")
translate_frame.pack(fill="x", pady=(20, 10))

translator_label = ctk.CTkLabel(translate_frame, text="Translate To:", font=("Arial", 16))
translator_label.pack(anchor="w", pady=(0, 5))

translate_controls = ctk.CTkFrame(translate_frame, fg_color="transparent")
translate_controls.pack(fill="x")

language_dropdown = ctk.CTkOptionMenu(
    translate_controls,
    values=["English", "Urdu", "French", "Spanish", "German", "Arabic", "Hindi", "Japanese", "Korean", "Dutch", "Turkish"],
    width=150
)
language_dropdown.pack(side="left", padx=(0, 10))

ctk.CTkButton(translate_controls, text="🌐 Translate", width=150, height=40, 
              command=translate_text).pack(side="left")

translated_result = ctk.CTkLabel(
    detect_page,
    text="Translated text will appear here...",
    font=("Arial", 16),
    wraplength=800,
    justify="left"
)
translated_result.pack(anchor="w", pady=(10, 0))

# ---------------- HISTORY PAGE ----------------

ctk.CTkLabel(history_page, text="Detection History", font=("Arial", 30, "bold")).pack(pady=20)

history_box = ctk.CTkTextbox(history_page, width=900, height=400)
history_box.pack(padx=20, pady=20, fill="both", expand=True)

history_button_frame = ctk.CTkFrame(history_page, fg_color="transparent")
history_button_frame.pack(pady=10)

ctk.CTkButton(history_button_frame, text="🗑 Clear History", fg_color="red", 
              hover_color="darkred", command=clear_history).pack(side="left", padx=5)

# ---------------- ABOUT PAGE ----------------

ctk.CTkLabel(about_page, text="About Language Detector Pro", font=("Arial", 30, "bold")).pack(pady=20)

about_text = """
Version: 2.1 (Improved)

Developed Using:
• Python 3.14
• CustomTkinter
• LangID
• Google Translate API
• pyttsx3 (Text-to-Speech)

Features:
• 🔍 Detect Multiple Languages
• 📊 Confidence Percentage
• 📝 Character Counter
• 📜 History Tracking (JSON Storage)
• 🔊 Text-to-Speech (with fallback)
• 🎤 Web-Based Speech-to-Text
• 🌐 Translation Support

Improvements in v2.1:
• Better TTS reliability with fallback
• Enhanced language detection
• More translation languages
• Better error handling

Speech-to-Text:
Uses web-based recognition (No PyAudio required!)
Opens Dictation.io in your browser

Developer:
Muhammad Saad

Semester Project - OSSD
"""

ctk.CTkLabel(about_page, text=about_text, justify="left", font=("Arial", 18)).pack(pady=20)

# ---------------- TTS INITIALIZATION (MOVED AFTER UI CREATION) ----------------

TTS_AVAILABLE = False
tts_engine = None

def init_tts():
    """Initialize TTS engine with retry mechanism"""
    global tts_engine, TTS_AVAILABLE
    try:
        # Try multiple backends
        try:
            tts_engine = pyttsx3.init(driverName='sapi5')  # Windows
        except:
            try:
                tts_engine = pyttsx3.init(driverName='nsss')  # Linux
            except:
                tts_engine = pyttsx3.init()  # Default
        
        if tts_engine:
            tts_engine.setProperty('rate', 150)
            tts_engine.setProperty('volume', 0.9)
            # Get available voices
            try:
                voices = tts_engine.getProperty('voices')
                if voices:
                    # Try to use a female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            tts_engine.setProperty('voice', voice.id)
                            break
            except:
                pass
            TTS_AVAILABLE = True
            root.after(0, lambda: tts_status.configure(text="✅ TTS Ready", text_color="green"))
    except Exception as e:
        TTS_AVAILABLE = False
        root.after(0, lambda: tts_status.configure(text=f"⚠️ TTS: Use external (click Speak)", text_color="orange"))

# Start TTS initialization in background thread
threading.Thread(target=init_tts, daemon=True).start()

# ---------------- LOAD HISTORY ON STARTUP ----------------

# Load existing history into the history box
for entry in history:
    history_box.insert("end", entry + "\n")

# ---------------- START APP ----------------

show_page("detect")
root.mainloop()