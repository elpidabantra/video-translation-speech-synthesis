#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:53:41 2024

@author: elpidabantra
"""

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from pydub import AudioSegment, effects
import speech_recognition as sr
import os
from googletrans import Translator
from gtts import gTTS

def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def preprocess_audio(input_audio_path, output_audio_path):
    audio = AudioSegment.from_file(input_audio_path)
    normalized_audio = effects.normalize(audio)
    filtered_audio = normalized_audio.low_pass_filter(3000)
    filtered_audio.export(output_audio_path, format="wav")

def transcribe_audio(audio_path, language='el-GR'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            transcript = recognizer.recognize_google(audio, language=language)
            return transcript
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

def translate_text(text, src='el', dest='en'):
    translator = Translator()
    translation = translator.translate(text, src=src, dest=dest)
    return translation.text

def synthesize_speech(text, language='en', output_audio_path='translated_audio.mp3'):
    tts = gTTS(text=text, lang=language)
    tts.save(output_audio_path)

def create_subtitled_video(video_path, translated_text, synthesized_audio_path, output_path):
    video = VideoFileClip(video_path)
    # Create a TextClip for subtitles
    subtitles = TextClip(translated_text, fontsize=24, color='white', bg_color='black', size=video.size, method='caption').set_position(('center', 'bottom')).set_duration(video.duration)
    
    # Load synthesized speech audio
    synthesized_audio = AudioFileClip(synthesized_audio_path).set_duration(video.duration)
    
    # Overlay the subtitles on the video and set the synthesized audio
    result = CompositeVideoClip([video, subtitles]).set_audio(synthesized_audio)
    result.write_videofile(output_path, codec='libx264', audio_codec='aac')

def transcribe_and_translate_video(video_path, language='el-GR', dest_languages=None):
    if dest_languages is None:
        dest_languages = ['es', 'de', 'ro', 'fr', 'zh-CN', 'hi', 'it', 'sv', 'sq']  # Spanish, German, Romanian, French, Chinese, Hindi, Italian, Swedish, Albanian
    language_names = {
        'es': 'Spanish',
        'de': 'German',
        'ro': 'Romanian',
        'fr': 'French',
        'zh-CN': 'Chinese',
        'hi': 'Hindi',
        'it': 'Italian',
        'sv': 'Swedish',
        'sq': 'Albanian'
    }

    audio_path = "extracted_audio.mp3"
    wav_audio_path = "extracted_audio.wav"

    print(f"Extracting audio from video: {video_path}")
    extract_audio_from_video(video_path, audio_path)

    print(f"Preprocessing audio: {audio_path}")
    preprocess_audio(audio_path, wav_audio_path)

    print(f"Transcribing audio: {wav_audio_path}")
    transcript = transcribe_audio(wav_audio_path, language=language)
    print(f"Transcript: {transcript}")

    for dest_language in dest_languages:
        print(f"Translating text to {language_names[dest_language]}")
        translated_text = translate_text(transcript, src='el', dest=dest_language)
        print(f"Translated Text ({language_names[dest_language]}): {translated_text}")

        synthesized_audio_path = f"translated_audio_{dest_language}.mp3"
        output_video_path = f"translated_video_{language_names[dest_language]}.mp4"

        print(f"Synthesizing speech in {language_names[dest_language]}")
        synthesize_speech(translated_text, language=dest_language, output_audio_path=synthesized_audio_path)

        print(f"Creating subtitled video in {language_names[dest_language]}: {output_video_path}")
        create_subtitled_video(video_path, translated_text, synthesized_audio_path, output_video_path)

        # Clean up temporary audio files
        os.remove(synthesized_audio_path)

    os.remove(audio_path)
    os.remove(wav_audio_path)

if __name__ == "__main__":
    video_path = "/Users/elpidabantra/myenvgenAI/ds_testing_video_gr.mp4"  # Change this to your video file path
    transcribe_and_translate_video(video_path)

