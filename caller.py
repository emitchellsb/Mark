#!/usr/bin/env python
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from PyDictionary import PyDictionary
from gtts import gTTS
import os
import sys
import subprocess
import pyaudio
import wave
import string
import time
import requests
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
        language_code='en-US')

    response = client.recognize(config, audio)
    
    return response

def get_response(response):
	transcript = ''
	for result in response.results:
		transcript += format(result.alternatives[0].transcript)
	return transcript

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
	else: 
		order_rating = 1000

	likeness = float((2*contains_rating + order_rating)/300)

	return likeness

def news(text):
	text = text.translate(None, string.punctuation)
	text = text.split(" ")
	for word in text:
		word = word.lower

	source_index = ['abc-news', 'abc-news-au', 'aftenposten', 'al-jazeera-english', 'ansa', 'argaam', 'ars-technica', 'ary-news', 'associated-press', 'australian-financial-review', 'axios', 'bbc-news', 'bbc-sport', 'bild', 'blasting-news-br', 'bleacher-report', 'bloomberg', 'breitbart-news', 'buisness-insider', 'business-insider-uk', 'buzzfeed', 'cbc-news', 'cbs-news', 'cnbc', 'cnn', 'cnn-es', 'crypto-coins-news', 'daily-mail', 'der-tagesspiegel', 'die-ziet', 'el-mundo', 'engadget', 'entertainment-weekly', 'espn', 'espn-cric-info', 'financial-post', 'financial-times', 'focus', 'footbal-italia', 'fortune', 'four-four-two', 'fox-news', 'fox-sports', 'globo', 'google-news', 'google-news-ar', 'google-news-au', 'google-news-br', 'google-news-ca', 'google-news-fr', 'google-news-in', 'google-news-is', 'google-news-it', 'google-news-ru', 'google-news-sa', 'google-news-uk', 'goteborgs-posten', 'gruenderszene', 'hacker-news', 'handelsblatt', 'ign', 'il-sole-24-ore', 'independent', 'infobae', 'info-money', 'la-gaceta', 'la-nacion', 'la-repubblica', 'le-monde', 'lenta', 'lequipe', 'les-echos', 'liberation', 'marca', 'mashable', 'medical-news-today', 'metro', 'mirror', 'msnbc', 'mtv-news', 'mtv-news-uk', 'national-geographic', 'nbc-news', 'news24', 'new-scientist', 'news-com-au', 'newsweek', 'new-york-magazine', 'next-big-future', 'nfl-news', 'nhl-news', 'nrk', 'politico', 'polygon', 'rbc', 'recode', 'reddit-r-all', 'reuterse', 'rt', 'rte', 'rtl-nieuws', 'sabq', 'spiegel-online', 'svenska-dagbladet', 't3n', 'talksport', 'techcrunch', 'techcrunch-cn', 'techradar', 'the-economist', 'the-globe-and-mail', 'the-guardian-au', 'the-guardian-uk', 'the-hill', 'the-hindu', 'the-huffington-post', 'the-irish-times', 'the-lad-bible', 'the-new-york-times', 'the-next-web', 'the-sport-bible', 'the-telegraph', 'the-times-of-india', 'the-verge', 'the-wall-street-journal', 'the-washington-post', 'time', 'usa-today', 'vice-news', 'wired', 'wired-de', 'wirtschafts-woche', 'xinhua-net', 'ynet']
	source_index_searchable = []
	for source in source_index:
		source_index_searchable.append(source.replace('-', ' '))
	
	source_tag = 'bbc-news'
	news_key = '379dd265f19d4465ae7a77cb30c2684f'
	source = 'bbc news'
	q = ''
	articles = 'The top 4 trending stories are: '
	num = 4
	max_num = 4
	desc_type = 0

	if ('from' in text or 'by' in text): #we have specified a source
		if ('on' in text or 'about' in text):
			desc_type = 3
			try:
				src_index = text.index('from')
			except:
				src_index = text.index('by')
			try:
				tpc_index = text.index('on')
			except:
				tpc_index = text.index('about')
			if (src_index < tpc_index): #news from __ on __
				i = src_index + 1
				if (i != tpc_index):
					source = ''
					while (i < tpc_index):
						source += text[i]
						i += 1
					#check source is real
					for source_s in source_index_searchable:
						if (source_s.find(source.lower()) != -1):
							source_tag = source_index[source_index_searchable.index(source_s)]
							break
				i = tpc_index + 1
				topic = ''
				if (i != len(text)):
					while (i < len(text)):
						topic += text[i]
						i += 1
					q = '&q='+topic

			else: #news on __ from __
				topic = ''
				i = tpc_index + 1
				if (i != src_index):
					while (i < src_index):
						topic += text[i]
						i += 1
					q = '&q='+topic
				i = src_index + 1
				if (i != len(text)):
					source = ''
					while (i < len(text)):
						source += text[i]
						i += 1
				#check source is real
				for source_s in source_index_searchable:
					if (source_s.find(source.lower()) != -1):
						source_tag = source_index[source_index_searchable.index(source_s)]
						break

		else:
			#just source
			desc_type = 1
			try:
				index = text.index('from')
			except:
				index = text.index('by')
			i = index+1
			if (i != len(text)):
				source = ''
				while (i < len(text)):
					source += text[i]
					i += 1
				#check source is real
				for source_s in source_index_searchable:
					if (source_s.find(source.lower()) != -1):
						source_tag = source_index[source_index_searchable.index(source_s)]
						break

	elif ('on' in text or 'about' in text):
		#just topic
		desc_type = 2
		try:
			index = text.index('on')
		except:
			index = text.index('about')
		topic = ''
		q = ''
		i = index+1
		if (i != len(text)):
			while (i < len(text)):
				topic += text[i]
				i += 1
			q += '&q='+topic


	url = ('https://newsapi.org/v2/top-headlines?sources='
       +source_tag+q+'&apiKey='+news_key)
	print(url)

	news = requests.get(url).json()

	if(news['status'] == 'ok'):
		if (desc_type != 0):
			num = 0
			news_read = ''
			for article in news['articles']:
				if(num < max_num):
					news_read += article['title'] + '. '
					num += 1
				else:
					break
			if (num != 0):
				if (desc_type == 1):
					articles = 'The top '+str(num)+' trending stories by '+source+' are: '+news_read
				elif (desc_type == 2):
					articles = 'The top '+str(num)+' trending stories about '+topic+' are: '+news_read
				elif (desc_type == 3):
					articles = 'The top '+str(num)+' trending stories by '+source+' about '+topic+' are: '+news_read
			else:
				articles = "I didn't find any articles, sorry mate."

		else:
			i = 0
			while(i < num):
				articles += news['articles'][i]['title'] + '. '
				i += 1
	else:
		articles = "I didn't find any articles, sorry mate."

	return articles

def cleverbot(text):
	API_KEY = 'CC5sziu110l1338RfLM-CPsPKHg'
	url = ('http://www.cleverbot.com/getreply?key='+API_KEY+'&input='+text+'&cs=76nxdxIJ02AAA')
	request = requests.get(url).json()
	return request['output']

def decide(text):
	likeness = isLike(['what', 'time'], text)
	if (likeness >= 8.0):
		return 'The current time is ' + time.ctime()
	likeness = isLike(['news'], text)
	if (likeness >= 8.0):
		return news(text)

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
		
		print('DECISION: ' + decision)

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
