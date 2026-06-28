import customtkinter as ctk
import langid
from datetime import datetime 
from deep_translator import GoogleTranslator
import pyttsx3
import threading
import webbrowser
import subprocess
import sys

# ---------------- APP SETTINGS ----------------

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Language Detector Pro")
root.geometry("1200x700")

history = []

# Initialize TTS engine
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('volume', 0.9)
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

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

    if len(text) < 5:
        result_lang.configure(text="Enter more text")
        confidence_label.configure(text="0%")
        progress.set(0)
        return

    lang, confidence = langid.classify(text)

    languages = {
        "en": "English", "ur": "Urdu", "fr": "French",
        "es": "Spanish", "de": "German", "ar": "Arabic",
        "hi": "Hindi", "ru": "Russian", "it": "Italian",
        "pt": "Portuguese", "zh": "Chinese"
    }

    language_name = languages.get(lang, lang)
    confidence_score = min(abs(confidence) * 10, 100)

    result_lang.configure(text=language_name)
    confidence_label.configure(text=f"{confidence_score:.1f}%")
    progress.set(confidence_score / 100)

    current_time = datetime.now().strftime("%H:%M:%S")
    history.append(language_name)
    history_box.insert("end", f"{current_time} | {language_name}\n")


def clear_text():
    textbox.delete("1.0", "end")
    counter.configure(text="Characters: 0")


def clear_history():
    history_box.delete("1.0", "end")
    history.clear()


def update_counter(event=None):
    chars = len(textbox.get("1.0", "end-1c"))
    counter.configure(text=f"Characters: {chars}")


def translate_text():
    text = textbox.get("1.0", "end").strip()
    
    if len(text) < 1:
        translated_result.configure(text="Please enter text to translate")
        return
    
    target_language = language_dropdown.get()
    
    lang_codes = {
        "English": "en", "Urdu": "ur", "French": "fr",
        "Spanish": "es", "German": "de", "Arabic": "ar",
        "Hindi": "hi"
    }
    
    target_code = lang_codes.get(target_language, "en")
    
    try:
        translator = GoogleTranslator(source='auto', target=target_code)
        translated = translator.translate(text)
        translated_result.configure(text=translated)
    except Exception as e:
        translated_result.configure(text=f"Translation error: {str(e)}")


def text_to_speech():
    if not TTS_AVAILABLE:
        tts_status.configure(text="❌ TTS not available", text_color="red")
        return
    
    text = textbox.get("1.0", "end").strip()
    
    if len(text) < 1:
        tts_status.configure(text="⚠️ No text to speak!", text_color="orange")
        return
    
    try:
        tts_status.configure(text="🔊 Speaking...", text_color="green")
        
        def speak():
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
                root.after(0, lambda: tts_status.configure(text="✅ Done!", text_color="green"))
            except Exception as e:
                root.after(0, lambda: tts_status.configure(text=f"❌ Error: {str(e)[:30]}", text_color="red"))
        
        threading.Thread(target=speak, daemon=True).start()
        
    except Exception as e:
        tts_status.configure(text=f"❌ Error: {str(e)[:30]}", text_color="red")


def stop_speech():
    try:
        if TTS_AVAILABLE:
            tts_engine.stop()
        tts_status.configure(text="⏹️ Stopped", text_color="orange")
    except:
        pass


def speech_to_text_browser():
    """Use browser-based speech recognition (no PyAudio needed)"""
    stt_status.configure(text="🌐 Opening speech recognition...", text_color="blue")
    
    # Open Google's speech recognition
    webbrowser.open("https://dictation.io/speech")
    
    # Show instructions
    dialog = ctk.CTkToplevel(root)
    dialog.title("🎤 Speech-to-Text Instructions")
    dialog.geometry("550x450")
    
    instructions = """
    🌐 **Web-Based Speech Recognition**
    
    ✅ No installation required!
    
    **How to use:**
    1. Browser will open Dictation.io
    2. Click "Start Dictation"
    3. Allow microphone access
    4. Speak clearly into your microphone
    5. Text will appear in browser
    6. Copy and paste text into app
    
    **Alternative Options:**
    
    🎯 **Google Docs** (Chrome only):
    • Open Google Docs
    • Tools → Voice Typing
    • Click microphone and speak
    
    📱 **Mobile Option**:
    • Use your phone's voice typing
    • Email or share the text
    
    🔧 **To install built-in STT later:**
    1. Install Visual C++ Build Tools
    2. Then: pip install pyaudio
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
        text="✓ Understood - Start Speaking",
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

# TTS Status
tts_status = ctk.CTkLabel(detect_page, text="🔊 Click 'Speak' to hear the text", font=("Arial", 14))
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
    values=["English", "Urdu", "French", "Spanish", "German", "Arabic", "Hindi"],
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

ctk.CTkButton(history_page, text="🗑 Clear History", fg_color="red", 
              hover_color="darkred", command=clear_history).pack(pady=10)

# ---------------- ABOUT PAGE ----------------

ctk.CTkLabel(about_page, text="About Language Detector Pro", font=("Arial", 30, "bold")).pack(pady=20)

about_text = """
Version: 2.0

Developed Using:
• Python 3.14
• CustomTkinter
• LangID
• Google Translate API
• pyttsx3 (Text-to-Speech)

Features:
• Detect Multiple Languages
• Confidence Percentage
• Character Counter
• History Tracking
• Modern GUI
• Text-to-Speech (TTS)
• Web-Based Speech-to-Text
• Translation Support

Speech-to-Text:
Uses web-based recognition (No PyAudio required!)
Opens Dictation.io in your browser

Developer:
Muhammad Saad

Semester Project
"""

ctk.CTkLabel(about_page, text=about_text, justify="left", font=("Arial", 18)).pack(pady=20)

# ---------------- START APP ----------------

show_page("detect")
root.mainloop()