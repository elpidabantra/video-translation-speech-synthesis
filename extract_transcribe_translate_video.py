#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:53:41 2024

@author: elpidabantra
"""


from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pydub import AudioSegment, effects
import speech_recognition as sr
import os
from googletrans import Translator

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

def create_subtitled_video(video_path, translated_text, output_path):
    video = VideoFileClip(video_path)
    # Create a TextClip for subtitles
    subtitles = TextClip(translated_text, fontsize=24, color='white', bg_color='black', size=video.size, method='caption').set_position(('center', 'bottom')).set_duration(video.duration)
    # Overlay the subtitles on the video
    result = CompositeVideoClip([video, subtitles])
    result.write_videofile(output_path, codec='libx264')

def transcribe_and_translate_video(video_path, language='el-GR'):
    audio_path = "extracted_audio.mp3"
    wav_audio_path = "extracted_audio.wav"
    output_video_path = "translated_video.mp4"

    print(f"Extracting audio from video: {video_path}")
    extract_audio_from_video(video_path, audio_path)

    print(f"Preprocessing audio: {audio_path}")
    preprocess_audio(audio_path, wav_audio_path)

    print(f"Transcribing audio: {wav_audio_path}")
    transcript = transcribe_audio(wav_audio_path, language=language)
    print(f"Transcript: {transcript}")

    print(f"Translating text to English")
    translated_text = translate_text(transcript, src='el', dest='en')
    print(f"Translated Text: {translated_text}")

    print(f"Creating subtitled video: {output_video_path}")
    create_subtitled_video(video_path, translated_text, output_video_path)

    # Clean up temporary audio files
    os.remove(audio_path)
    os.remove(wav_audio_path)

    return output_video_path

if __name__ == "__main__":
    video_path = "/Users/elpidabantra/myenvgenAI/ds_testing_video_gr.mp4"  # Change this to your video file path
    transcribed_video = transcribe_and_translate_video(video_path)
    print(f"Subtitled video saved as: {transcribed_video}")
