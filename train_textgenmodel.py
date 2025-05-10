#!/usr/bin/python3

# Initial version obtained with assistance of Claude 3.7 Sonnet
# and following
# https://debuggercafe.com/fine-tuning-gpt2-for-text-generation/
# https://huggingface.co/docs/transformers/en/tasks/language_modeling
# https://huggingface.co/learn/nlp-course/en/chapter7/6?fw=pt#training-a-causal-language-model-from-scratch


import datasets
from datasets import Dataset
import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments
# from transformers.loss.loss_utils import ForCausalLMLoss # default already...
import torch

import os
import random
import secrets


random.seed(secrets.randbits(0x20))
transformers.set_seed(secrets.randbits(0x20)) # in fact, this is to _avoid_ deterministic outputs...


BATCH_SIZE = 0x18 # samples
BLOCK_SIZE = 0x100 # tokens
BLOCK_STEP = 0x100 # tokens. It < BLOCK_SIZE means overlap
CORPUS_DIRPATH = 'text_corpus'
CUSTOM_INIT_TOKENIZER = True
DEFAULT_TEST_PART = 0.03
# EVAL_STEPS = LOGGING_STEPS
GRADIENT_ACCUMULATION_STEPS = 8
# LEARNING_RATE = 5e-5 # default for AdamW optimiser
LOCAL_MODEL_DIRNAME = '_textgenmodel_'
LOGGING_STEPS = 50 # checkpoint is saved every this number of steps
# LR_SCHEDULER_TYPE = "linear" # default, but some recommend "constant" for this modality
MAX_NEW_TOKENS = 0x100 # at final generation
# MAX_STEPS = 1024
METRIC_FOR_BEST_MODEL = 'eval_loss'
NUM_EPOCHS = 59 # 0 to skip training (already trained) local model and generate using it
NUM_FINAL_GENERATIONS = 3
# OPTIMISER = "adamw_torch" # default

PRETRAINED_MODEL_NAMEPATH = 'openai-community/gpt2'
# Alternatives (roughly, size increases; ⚠️ - executes remote code):
#   Intel/tiny-random-gpt2
#   erwanf/gpt2-mini
#   lgaalves/gpt2-dolly
#   anton-l/gpt-j-tiny-random
#   distilbert/distilgpt2
#   facebook/opt-125m
#   ⚠️facebook/MobileLLM-125M
#   openai-community/gpt2
#   EleutherAI/gpt-neo-125m
#   facebook/opt-350m
#   ⚠️facebook/MobileLLM-350M
# ... see https://huggingface.co/models

PROMPT1 = 'Быть иль не быть Вот в чём вопрос Что лучше Сносить ли от неистовой судьбы Удары стрел и камней или смело Вооружиться против моря зла И в бой вступить Ведь умереть уснуть Не больше И сознать что этим сном Мы заглушим все муки духа боли Телесные О это столь желанный Конец Да умереть уснуть Уснуть Жить в мире грёз быть может Вот Преграда А какие в мёртвом сне Видения пред духом бестелесным проносятся О в этом вся причина Что скорби долговечны на земле' # 'Hamlet'
PROMPT2 = 'Белеет пена дует ветр За нами рябь растёт Вошли мы первыми в просторы тех молчаливых вод Стих ветр и парус наш повис И горе к нам идёт Лишь голос наш звучит в тиши Тех молчаливых вод В горячих медных небесах Полдневною порой Над мачтой Солнце точно кровь С Луну величиной За днями дни за днями дни Мы ждём корабль наш спит Как в нарисованной воде Рисованный стоит Вода вода одна вода Но чан лежит вверх дном Вода вода одна вода Мы ничего не пьём' # 'The Rime of the Ancient Mariner'

RANDOM_INIT_WEIGHTS = True
SAVE_STEPS = LOGGING_STEPS
SAVE_TOTAL_LIMIT = 1 # 0 to keep only the best model, without the latest
STRATEGY='steps'
TOKENIZER_DIRNAME = '_tokenizer_'
TEMPERATURE = 1.0

TRUST_REMOTE_CODE = True # True is ⚠️SECURITY ISSUE⚠️, but may be the only way...

USE_KV_CACHE = True


def stack_slice_shuffle_split(dataset, test_part=DEFAULT_TEST_PART):
    print('Stacking... ', end='', flush=True)
    input_ids = dataset['input_ids']
    buffer = []
    for row in input_ids:
        buffer += row

    print(f"slicing (overlap mult. {BLOCK_SIZE // BLOCK_STEP})... ", end='', flush=True)
    sliced_input_ids = []
    offset = 0
    while offset + BLOCK_SIZE <= len(buffer):
        sliced_input_ids += [buffer[offset:(offset + BLOCK_SIZE)]]
        offset += BLOCK_STEP

    print('shuffling... ', end='', flush=True)
    random.shuffle(sliced_input_ids)

    print('splitting... ', end='', flush=True)
    train_len = max(1, min(len(sliced_input_ids) - 1, int((1.0 - test_part) * len(sliced_input_ids))))
    print('OK.', flush=True)

    return Dataset.from_dict({'input_ids' : sliced_input_ids[:train_len]}), Dataset.from_dict({'input_ids' : sliced_input_ids[train_len:]})


if os.path.isdir(LOCAL_MODEL_DIRNAME): # continue usage of local model
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIRNAME)
    model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_DIRNAME)
else:
    if CUSTOM_INIT_TOKENIZER:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIRNAME)
    else:
        tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAMEPATH, use_fast=False, trust_remote_code=TRUST_REMOTE_CODE)

    if RANDOM_INIT_WEIGHTS:
        config = AutoConfig.from_pretrained(
            PRETRAINED_MODEL_NAMEPATH,
            vocab_size=tokenizer.vocab_size,

            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=tokenizer.eos_token_id,

            trust_remote_code=TRUST_REMOTE_CODE
        )
        model = AutoModelForCausalLM.from_config(config)
    else:
        model = AutoModelForCausalLM.from_pretrained(PRETRAINED_MODEL_NAMEPATH, trust_remote_code=TRUST_REMOTE_CODE)

tokenizer.pad_token = tokenizer.eos_token

if NUM_EPOCHS > 0:

    dataset_train_tokenized, dataset_test_tokenized = stack_slice_shuffle_split(datasets.load_dataset('text', data_files=f"{CORPUS_DIRPATH}/*")['train'].map(lambda examples: tokenizer(examples['text']), batched=True))
    print(f"Train samples: {len(dataset_train_tokenized['input_ids'])}", flush=True)
    print(f"Test samples: {len(dataset_test_tokenized['input_ids'])}", flush=True)

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Not using masked language modeling for GPT-2
    )

    training_args = TrainingArguments(
        output_dir=LOCAL_MODEL_DIRNAME,
        overwrite_output_dir=True,
        num_train_epochs=NUM_EPOCHS,
        # max_steps=MAX_STEPS, # overrides num_train_epochs...
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        save_strategy=STRATEGY, # or "no"
        save_steps=SAVE_STEPS,
        save_total_limit=SAVE_TOTAL_LIMIT, # Keep fewer checkpoints to save disk space
        save_only_model=True,
        prediction_loss_only=True,
        eval_strategy=STRATEGY,
        # eval_steps=EVAL_STEPS, # defaults to logging_steps
        logging_strategy=STRATEGY,
        logging_steps=LOGGING_STEPS,
        load_best_model_at_end=True,
        metric_for_best_model=METRIC_FOR_BEST_MODEL,
        fp16=False,  # Mixed precision decreases memory usage
        # dataloader_num_workers=os.cpu_count(),
        # optim=OPTIMISER,
        # lr_scheduler_type=LR_SCHEDULER_TYPE,
        # learning_rate = LEARNING_RATE,
        # use_cpu=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset_train_tokenized,
        eval_dataset=dataset_test_tokenized
    )

    trainer.train()

    trainer.save_model() # may save tokenizer in output_dir as well...

    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIRNAME)
    tokenizer.pad_token = tokenizer.eos_token


pipe = transformers.pipeline(
    task='text-generation', 
    model=model, 
    tokenizer=tokenizer, 
    max_new_tokens=MAX_NEW_TOKENS
)


penult_replique = PROMPT1.split(' ')
random.shuffle(penult_replique)
penult_replique = ' '.join(penult_replique) + ' '

last_replique = PROMPT2.split(' ')
random.shuffle(last_replique)
last_replique = ' '.join(last_replique)

for _ in range(NUM_FINAL_GENERATIONS):
    prompt = penult_replique + last_replique
    penult_replique = last_replique
    last_replique = pipe(prompt, do_sample=True, temperature=TEMPERATURE, use_cache=USE_KV_CACHE)[0]['generated_text'][len(prompt):]
    print(last_replique)
