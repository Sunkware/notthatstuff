#!/usr/bin/python3

import torch

from TTS.api import TTS
print('Imported Coqui-TTS module.', flush=True)

import glob
import os
import shutil


EMBEDDING_FILENAME = 'embedding.pt'
LATENT_FILENAME = 'latent.pt'
SPEECHGEN_DIRNAME = '_speechgen_'
SPEECH_DIRNAME = 'speech_corpus'
TTS_MODEL_NAMEPATH = 'tts_models/multilingual/multi-dataset/xtts_v2'


tts = TTS(TTS_MODEL_NAMEPATH).to('cuda' if torch.cuda.is_available() else 'cpu')
print('Loaded model.', flush=True)

voice_sample_filepaths = glob.glob(f"{SPEECH_DIRNAME}/*")

gpt_cond_latent, speaker_embedding = tts.synthesizer.tts_model.get_conditioning_latents(audio_path=voice_sample_filepaths)
print('Computed speaker parameters.')

if os.path.isdir(SPEECHGEN_DIRNAME):
	shutil.rmtree(SPEECHGEN_DIRNAME)

if not os.path.isdir(SPEECHGEN_DIRNAME):
	os.mkdir(SPEECHGEN_DIRNAME)

torch.save(gpt_cond_latent, f"{SPEECHGEN_DIRNAME}/{LATENT_FILENAME}")
torch.save(speaker_embedding, f"{SPEECHGEN_DIRNAME}/{EMBEDDING_FILENAME}")
print('Saved speaker parameters.')
