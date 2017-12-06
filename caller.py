#!/usr/bin/env python
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
import pyttsx
import os
import sys
import subprocess
import pyaudio
import wave

def record():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16 #paInt8
	CHANNELS = 1 
	RATE = 44100 #sample rate
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = "input.wav"

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
	                frames_per_buffer=CHUNK) #buffer

	print("Recording")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data) # 2 bytes(16 bits) per channel

	print("Done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def transcribe_file(speech_file):
    # Transcribe the given audio file.
    credentials = service_account.Credentials.from_service_account_file('settings/Mark-341e0729698c.json')

    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

    client = speech.SpeechClient()

    with open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US') #CHECK THIS

    response = client.recognize(config, audio)
    # Print the first alternative of all the consecutive results.
    #for result in response.results:
        #print('Transcript: {}'.format(result.alternatives[0].transcript))
    
    return response

def tts(response):
	transcript = ''
	for result in response.results:
		transcript += format(result.alternatives[0].transcript) 

	print(transcript)

	engine = pyttsx.init()
	engine.say(transcript)
	engine.runAndWait()

def main():

	# Initialise:
	filename = "input.wav"

	while(1):
		# Step 1: Call java program to get audio input
		record()
		# Step 2: Call transcribe_file function to make API request
		response = transcribe_file(filename)

		# Step 3: Read text response and confidence level
		tts(response)

		# Step 4: Decide on action and response
		# Step 5: Perform action
		# Step 6: Respond
		# Step 7: Clear data (delete audio file, etc)
		# Step 8: Wait for input to start next loop or close
		break

if __name__ == "__main__":
	main()

#INSTRUCTIONS:
#NEED TO INSTALL: easy_install pyaudio
