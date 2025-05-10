#!/usr/bin/python3

# Based on https://huggingface.co/learn/nlp-course/en/chapter6/8?fw=pt#building-a-bpe-tokenizer-from-scratch

from tokenizers import decoders, models, pre_tokenizers, processors, trainers, Tokenizer
from transformers import GPT2TokenizerFast

import glob


CORPUS_DIRPATH = 'text_corpus'
TOKENIZER_DIRNAME = '_tokenizer_'
VOCAB_SIZE = 0xC000 # more? less? see e.g. https://www.rohan-paul.com/p/tutorial-balancing-vocabulary-size


tokenizer = Tokenizer(models.BPE())

tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)

trainer = trainers.BpeTrainer(vocab_size=VOCAB_SIZE, special_tokens=['<|endoftext|>'])

tokenizer.model = models.BPE()

corpus_filepaths = glob.glob(f"{CORPUS_DIRPATH}/*")

tokenizer.train(corpus_filepaths, trainer=trainer)

tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)

tokenizer.decoder = decoders.ByteLevel()

wrapped_tokenizer = GPT2TokenizerFast(tokenizer_object=tokenizer)

wrapped_tokenizer.save_pretrained(TOKENIZER_DIRNAME)