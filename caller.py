#!/usr/bin/env python
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from PyDictionary import PyDictionary
from gtts import gTTS
import requests
import os
import sys
import subprocess
import pyaudio
import wave
import string
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

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
    credentials = service_account.Credentials.from_service_account_file('./settings/Mark-341e0729698c.json')

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
    
    return response

def isLike(keywords, text): #keywords is an ORDERED array of strings, input is the text input of the user
	likeness = 0
	text = text.translate(None, string.punctuation)
	text = text.split(" ")
	for word in text:
		word = word.lower
	for word in keywords:
		word = word.lower

	num_contains = 0
	included_arr = []
	for word in keywords:
		synonyms = PyDictionary.synonym(word)
		if(synonyms == None):
			synonyms = []
		else:
			for synonym in synonyms:
				synonym = str(synonym)
		synonyms.extend([word, word+'s'])	
		for synonym in synonyms:
			if (synonym in text):
				included_arr.append(word)
				num_contains += 1
				break
	contains_rating = int(1000*num_contains/len(keywords))

	used_keywords = []
	for word in keywords:
		if (word in included_arr):
			used_keywords.append(word)
	
	if(len(used_keywords) > 1):	
		total_precedes = 0
		i = len(used_keywords) - 1
		while (i >= 1):
			total_precedes += i
			i -= 1
		num_precedes = 0
		length = len(used_keywords)
		i = 0
		while (i < length):
			word1 = used_keywords[i]
			j = i+1
			while (j < length):
				word2 = used_keywords[j]
				if (included_arr.index(word1) < included_arr.index(word2)):
					num_precedes += 1
				j += 1
			i += 1

		order_rating = int(1000*num_precedes/total_precedes)

		likeness = float((2*contains_rating + order_rating)/300)

	return likeness

def get_response(response):
	transcript = ''
	for result in response.results:
		transcript += format(result.alternatives[0].transcript)
	return transcript

def cleverbot(text):
	API_KEY = 'CC5sziu110l1338RfLM-CPsPKHg'
	url = ('http://www.cleverbot.com/getreply?key='+API_KEY+'&input='+text+'&cs=76nxdxIJ02AAA')
	request = requests.get(url).json()
	return request['output']

def decide(text):
	likeness = isLike(['what', 'time'], text)
	if (likeness >= 8.0):
		return 'The current time is ' + time.ctime()

	return cleverbot(text)

def tts(output):

	tts = gTTS(text=output, lang='en-au')
	tts.save('output.mp3')
	os.system('mpg321 output.mp3')

def main():

	# Initialise:
	filename = "input.wav"

	while(1):
		# Step 1: Get audio input
		record()
		# Step 2: Call transcribe_file function to make API request
		response = transcribe_file(filename)

		# Step 3: Read text response
		text = str(get_response(response))
		print(text)

		# Step 4: Decide on action and response
		decision = decide(text)
		
		tts(decision)
		# Step 5: Perform action
		# Step 6: Respond
		# Step 7: Clear data (delete audio file, etc)
		# Step 8: Wait for input to start next loop or close
		break

if __name__ == "__main__":
	main()

#INSTRUCTIONS:
#NEED TO INSTALL: easy_install pyaudio
