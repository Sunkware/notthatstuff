#!/usr/bin/python3


DO_SPEECH = True


import soundfile
import torch
# import torchaudio
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

if DO_SPEECH:
	from TTS.api import TTS
	print('Imported Coqui-TTS module.', flush=True)

import glob
import json
import os
import random
import secrets
import shutil
import time


CHATTER_SEED1 =  'Быть иль не быть Вот в чём вопрос Что лучше Сносить ли от неистовой судьбы Удары стрел и камней или смело Вооружиться против моря зла И в бой вступить Ведь умереть уснуть Не больше И сознать что этим сном Мы заглушим все муки духа боли Телесные О это столь желанный Конец Да умереть уснуть Уснуть Жить в мире грёз быть может Вот Преграда А какие в мёртвом сне Видения пред духом бестелесным проносятся О в этом вся причина Что скорби долговечны на земле' # 'To be or not to be?''
CHATTER_SEED2 = 'Белеет пена дует ветр За нами рябь растёт Вошли мы первыми в просторы тех молчаливых вод Стих ветр и парус наш повис И горе к нам идёт Лишь голос наш звучит в тиши Тех молчаливых вод В горячих медных небесах Полдневною порой Над мачтой Солнце точно кровь С Луну величиной За днями дни за днями дни Мы ждём корабль наш спит Как в нарисованной воде Рисованный стоит Вода вода одна вода Но чан лежит вверх дном Вода вода одна вода Мы ничего не пьём' # 'Ancient Mariner'
DEFAULT_SPEECH_TEMPERATURE = 0.75 # Coqui's XTTS default (documentation mentions 0.65, but see actual inference() in tts/models/xtts.py)
DEFAULT_SPEED = 1.0 # speech
DEFAULT_TEXT_TEMPERATURE = 1.0
DO_SHUFFLE_CHATTER_SEED = True
EMBEDDING_FILENAME = 'embedding.pt'
IDLERATE = 100
LANGUAGE = 'ru'
LATENT_FILENAME = 'latent.pt'
NEW_REPLIQUE_DIRNAME = 'new'
PARAMETERS_FILENAME = 'parameters.json'
REPLIQUES_DIRNAME = '_repliques_'
REPLIQUES_RESERVE_LEN = 0x10 # or 1440 ~ 1 day
SAMPLE_RATE = 24000 # Coqui's XTTS default
SPEAKER_FILENAME = 'speaker.txt'
SPEAKERS_DIRNAME = 'speakers'
# SPEECH_DIRNAME = 'speech_corpus'
SPEECH_FILENAME = 'speech.flac'
SPEECHGEN_DIRNAME = '_speechgen_'
TEXT_FILENAME = 'text.txt'
TEXT_LENGTH_MIN = 0x80 # tokens
TEXT_LENGTH_MAX = 0x100 # tokens, (BLOCK_SIZE >> 1) in train_textgenmodel.py
TEXTGEN_MODEL_DIRNAME = '_textgenmodel_'
TTS_MODEL_NAMEPATH = 'tts_models/multilingual/multi-dataset/xtts_v2'
# TTS_MODEL_NAMEPATH = "tts_models/rus/fairseq/vits" # DEBUG (without cloning)
USE_KV_CACHE = True


class Parameters:

	def __init__(self, speaker_dirpath):
		params = dict()
		try:
			with open(f"{speaker_dirpath}/{PARAMETERS_FILENAME}", 'r') as file:
				params = json.loads(file.read())
		except:
			pass
		if 'speech_temperature' in params.keys():
			self.speech_temperature = params['speech_temperature']
		else:
			self.speech_temperature = DEFAULT_SPEECH_TEMPERATURE
		if 'speed' in params.keys():
			self.speed = params['speed']
		else:
			self.speed = DEFAULT_SPEED
		if 'text_temperature' in params.keys():
			self.text_temperature = params['text_temperature']
		else:
			self.text_temperature = DEFAULT_TEXT_TEMPERATURE


class SpeechGenerator:

	def __init__(self, speaker_dirpath):
		self.latent = torch.load(f"{speaker_dirpath}/{SPEECHGEN_DIRNAME}/{LATENT_FILENAME}")
		self.embedding = torch.load(f"{speaker_dirpath}/{SPEECHGEN_DIRNAME}/{EMBEDDING_FILENAME}")


class TextGenerator:

	def __init__(self, speaker_dirpath):
		model_dirpath = f"{speaker_dirpath}/{TEXTGEN_MODEL_DIRNAME}"
		self.model = AutoModelForCausalLM.from_pretrained(model_dirpath)
		self.tokenizer = AutoTokenizer.from_pretrained(model_dirpath)
		self.tokenizer.pad_token = self.tokenizer.eos_token


	def generate_text(self, prompt, temperature=DEFAULT_TEXT_TEMPERATURE):
		pipe = pipeline(task='text-generation', model=self.model, tokenizer=self.tokenizer, max_new_tokens=TEXT_LENGTH_MIN + secrets.randbelow(1 + TEXT_LENGTH_MAX - TEXT_LENGTH_MIN))
		return pipe(prompt, do_sample=True, temperature=temperature, use_cache=USE_KV_CACHE)[0]['generated_text'][len(prompt):]


def str_seed_shuffle(seed, shuffle=False):
	s = seed.split(' ')
	if shuffle:
		random.shuffle(s)
	return ' '.join(s)


def run():
	if not os.path.isdir(REPLIQUES_DIRNAME):
		os.mkdir(REPLIQUES_DIRNAME)

	new_rpl_dirpath = f"{REPLIQUES_DIRNAME}/{NEW_REPLIQUE_DIRNAME}"

	if os.path.isdir(new_rpl_dirpath):
		shutil.rmtree(new_rpl_dirpath)

	os.chdir(REPLIQUES_DIRNAME)
	dirnames = glob.glob('*')
	os.chdir('..')

	i = 0
	for dirname in dirnames:
		try:
			n = int(dirname)
			i = max(i, n)
		except ValueError:
			pass
	try:
		with open(f"{REPLIQUES_DIRNAME}/{i}/{TEXT_FILENAME}", 'r') as file:
			last_replique = file.read() # continue "conversation" instead of reset it
		with open(f"{REPLIQUES_DIRNAME}/{i-1}/{TEXT_FILENAME}", 'r') as file:
			penult_replique = file.read()
	except: # dir(s) do not exist (e.g. when i==0) or file cannot be opened or ...
		penult_replique = str_seed_shuffle(CHATTER_SEED1, DO_SHUFFLE_CHATTER_SEED)
		last_replique = str_seed_shuffle(CHATTER_SEED2, DO_SHUFFLE_CHATTER_SEED)
	i += 1

	if DO_SPEECH:
		tts = TTS(TTS_MODEL_NAMEPATH).to('cuda' if torch.cuda.is_available() else 'cpu')
		print(f"Initialised TTS: {TTS_MODEL_NAMEPATH}.", flush=True)

	os.chdir(SPEAKERS_DIRNAME)
	speakers = glob.glob('*')
	os.chdir('..')
	print(f"Found {len(speakers)} speakers {speakers} ", end='', flush=True)

	time.sleep(1.0 / IDLERATE)

	parameters = dict()
	if DO_SPEECH:
		speechgens = dict()
	textgens = dict()
	for speaker in speakers:
		parameters[speaker] = Parameters(f"{SPEAKERS_DIRNAME}/{speaker}")
		if DO_SPEECH:
			speechgens[speaker] = SpeechGenerator(f"{SPEAKERS_DIRNAME}/{speaker}")
		textgens[speaker] = TextGenerator(f"{SPEAKERS_DIRNAME}/{speaker}")
	print('and loaded their generation models & parameters.', flush=True)

	while True:
		if len(glob.glob(f"{REPLIQUES_DIRNAME}/*")) < REPLIQUES_RESERVE_LEN:
			os.mkdir(new_rpl_dirpath) # so that Player won't read it until it's ready

			speaker = secrets.choice(speakers)
			with open(f"{new_rpl_dirpath}/{SPEAKER_FILENAME}", 'w') as file:
				file.write(speaker)

			prompt = penult_replique + last_replique
			penult_replique = last_replique
			last_replique = textgens[speaker].generate_text(prompt, parameters[speaker].text_temperature)
			with open(f"{new_rpl_dirpath}/{TEXT_FILENAME}", 'w') as file:
				file.write(last_replique) # for Player, but it also can be read above if Forger is resumed

			# DEBUG (without cloning)
			# sound = tts.tts_to_file(last_replique, file_path=f"{new_repl_dirpath}/{SPEECH_FILENAME}")

			""" DEBUG (clone on-the-fly, without precomputed latent & embedding)
			voice_sample_filepaths = glob.glob(f"{SPEAKERS_DIRNAME}/{speaker}/{SPEECH_DIRNAME}/*")
			tts.tts_to_file(
				last_replique,
				speaker_wav=voice_sample_filepaths,
				language=LANGUAGE,
				file_path=f"{new_rpl_dirpath}/{SPEECH_FILENAME}",
				enable_text_splitting=True, # to avoid "overflow" of TTS model on too long sentences
				speed=parameters[speaker].speed,
				temperature=parameters[speaker].speech_temperature
			)
			"""

			if DO_SPEECH:
				speech = tts.synthesizer.tts_model.inference(
					last_replique,
					LANGUAGE,
					speechgens[speaker].latent,
					speechgens[speaker].embedding,
					enable_text_splitting=True, # to avoid "overflow" of TTS model on too long sentences
					speed=parameters[speaker].speed,
					temperature=parameters[speaker].speech_temperature
				)
				soundfile.write(f"{new_rpl_dirpath}/{SPEECH_FILENAME}", speech['wav'], SAMPLE_RATE)

			os.rename(new_rpl_dirpath, f"{REPLIQUES_DIRNAME}/{i}") # now Playeraser can read it, play, and then erase

			print(f"Forged replique {i}.", flush=True)

			i += 1

		time.sleep(1.0 / IDLERATE)


if __name__ == '__main__':
	random.seed(secrets.randbits(0x20))
	transformers.set_seed(secrets.randbits(0x20))
	run()
