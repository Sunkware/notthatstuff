⚠️ **DEEPFAKEHAZARD** 🤥

# not &ensp; that &ensp; stuff

is based on illustrious [The Infinite Conversation](https://www.infiniteconversation.com/) from Giacomo Miceli, described also on [his site](https://jamez.it/project/the-infinite-conversation/) and in [Scientific American article](https://www.scientificamerican.com/article/what-an-endless-conversation-with-werner-herzog-can-teach-us-about-ai/), — [Large-language-model](https://en.wikipedia.org/wiki/Large_language_model) + [Text-to-speech](https://en.wikipedia.org/wiki/Speech_synthesis) + [Voice-cloning](https://en.wikipedia.org/wiki/Audio_deepfake) [doppelgängers](https://en.wikipedia.org/wiki/Doppelg%C3%A4nger) of more or less famous real persons, trained on respective genuine contents produced by them, exchange plausible written and spoken repliques for as long as someone is able and willing to run the generators. At least, the goal is to (re)implement the concept... yet another time.

See and hear it in action at [sunkware.org/yau/nts](https://sunkware.org/yau/nts/index.php), — haven't you come here from there, — where, instead of "[Werner Herzog](https://en.wikipedia.org/wiki/Werner_Herzog)" and "[Slavoj Žižek](https://en.wikipedia.org/wiki/Slavoj_%C5%BDi%C5%BEek)" of the original, who discuss art and philosophy, it brings together ("" of) several so-called "experts" or "commentators" after monological videos from their YouTube channels, where they mostly comment on [unprovoked full-scale russian invasion upon Ukraine](https://en.wikipedia.org/wiki/Russian_invasion_of_Ukraine).

Now, we suppose, you are interested in its

## Usage

consists of *training stage*, *generation stage*, and *playing stage*.

But first of all, you find at least 2 *speakers* whose dialogue you want to imitate... assuming they have produced enough content required for

### Training stage

proceeds independently for each speaker, from whom you need to obtain

* *text corpus*: many plain text (`.txt`) files in UTF-8 encoding, their total size being not less than 10 MB (the more **of good quality**, the better). Put them all into `SpeakerName/text_corpus/`.

* *speech corpus*: several audio files with **clean** speech, each one approximately 30 sec in duration. All common formats such as `.ogg`, `.mp3`, `.flac`, `.wav` should work. They go into `SpeakerName/speech_corpus/`.

For any given speaker, these 2 corpora may be completely unrelated.

**The quality of corpora is essential** (who would've thought). Entire content should belong to the speaker at hand, be strictly her or his, so, for example, a dialogue with someone else, even if her or his part is 99% of it, does not satisfy this requirement. You aim for 100%, therefore seek a **monologue**. There is an exception for *quotes*, regarding speech more than text, because when they quote other people, we can still extract the characteristics of *their voices*. Remove all headers and titles such as "Part 7", "Purgatory Kept", "MDCCXLVI", footnotes and so on, leaving only **direct speech**.

How exactly you obtain these corpora and what courtesy they will have (and how many *lawyers* will be after you) varies... See `getplainsubs_batch.sh` and `getaudio.sh`, — for our purposes we used YouTube and [yt-dlp](https://github.com/yt-dlp/yt-dlp) downloader to obtain plain subtitles and audio tracks. From the latter we then cut 30-sec fragments in [Audacity](https://www.audacityteam.org/). Published (thus spell-checked) textual works such as books and articles usually have much better quality (i.e. punctuation marks) than subtitles, so try to get them; they, too, may require cleaning, see `cleantext.sh`.

All corpora must be in the same language, [supported by XTTS-v2](https://coqui-tts.readthedocs.io/en/latest/models/xtts.html#languages) of [Coqui-TTS](https://github.com/idiap/coqui-ai-tts) or another text-to-speech and voice-cloning model you are going to use.

GPU with CUDA support and enough VRAM is almost necessary for training to take days instead of months; as for generation, CPU-only way is possible if you are able to afford waiting, in particular when you do not need generation to be faster than listening. There are many cloud GPU providers out there anxious to get your 💰 (we've rented 1-GPU instance with 16 GB VRAM for approx. $7/day at [RunPod](https://www.runpod.io/)). See `cloud_deploy.sh` as an example of additional setup of a remote computational instance to which you have SSH access; in particular, you need a terminal multiplexer such as `tmux` for training to continue when you logout. That instance either runs continuously until the end of generation stage, or it has some persistent storage keeping the intermediate results during reboots.

```shell
$ pip install --upgrade accelerate coqui-tts datasets sounddevice soundfile torch transformers
```

Place symlinks to `train_speechgen.py`, `train_tokenizer.py`, `train_textgenmodel.py` to `SpeakerName` dir, which by now already has `text_corpus/` and `speech_corpus/` inside.

From `SpeakerName/`

```shell
$ python3 train_speechgen.py
```

Wait for a minute or so. `_speechgen_` dir with two `.pt` files appears.

```shell
$ python3 train_tokenizer.py
```

In less than a minute, `_tokenizer_` dir is ready. Now comes the longest part...

```shell
$ python3 train_textgenmodel.py
```

Depending on the model, the size of text corpus, and the number (and type) of GPU(s) in your disposal, this part lasts from several hours to couple of days. In the end, `_textgenmodel_` dir, typically several hundreds of MB in size, contains a trained model (to be more precise, the checkpoint with the smallest evaluation loss) and the copy of tokenizer from previous step. In addition, there is one `checkpoint-..../`, which you can safely remove, and `runs/` to feed to [TensorBoard](https://www.tensorflow.org/tensorboard) in case you want to analyse the details of training process, e.g. when overfitting began.

At the end, trained model generates certain amount of text. Read it to estimate the model's "preparedness" to participate in a "conversation" with its sisters and brothers down the line. Maybe the training must continue. Or maybe you customise the process via

#### Training parameters

are gathered at the beginning of aforementioned Python scripts. In particular, pay attention to

* `VOCAB_SIZE` (49152 = 0xC000 by default)

from `train_tokenizer.py`. If you start to train the model with certain tokenizer, the model's internal state becomes "entangled" with this particular tokenizer, so in subsequent trainings and generations **only this one** must be used (break this rule to enjoy errors or garbage).

Also, in `train_textgenmodel.py`, there are

* `PRETRAINED_MODEL_NAMEPATH` (`openai-community/gpt2` by default, the smallest 124M-parameters version) and `RANDOM_INIT_WEIGHTS` (`True` by default)

* `BLOCK_SIZE` (context length in tokens, default is 256)

* `BLOCK_STEP` (256), if less than `BLOCK_SIZE`, makes blocks overlap; beware overfitting in such case

* `NUM_EPOCHS` (59)

* `BATCH_SIZE` (24) and `GRADIENT_ACCUMULATION_STEPS` (8)

Keep in mind that the larger `VOCAB_SIZE`, `BLOCK_SIZE`, and `BATCH_SIZE` you set, the more VRAM you need. For instance, these defaults require 15+ GB.

As usual, halt training via Ctrl+C as soon as `eval_loss` begins to *increase steadily*, which means overfitting. At that, `_textgenmodel_/` has no files, but 2 dirs named `checkpoint-...`: the best with lower index and the latest with higher index. Move all files from the best one to `_textgenmodel_` and remove the latest checkpoint. Or wait until the whole training completes, then it happens automatically (remove remaining checkpoint to free space).

Models for different speakers can be different, say, [`distilgpt2`](https://huggingface.co/EleutherAI/gpt-neo-125m) for some and [`gpt2`](https://huggingface.co/openai-community/gpt2) for others. When all models have been trained, you are ready for

### Generation stage

assumes you have `_speechgen_/` and `_textgenmodel_/` in each `SpeakerName/`.

`_tokenizer_`, `text_corpus/` and `speech_corpus` are unnecessary at this stage, but of course you keep them for later (re)training.

Move all `SpeakerName/`-s, or put symlinks to them, to `YourNTS/speakers` dir. And place symlink to `forger.py` into `YourNTS/`.

```
.../YourNts/
    ├─ speakers/
    │  ├─ Speaker_1_Name/
    │  │  ├─ _speechgen_/
    │  │  └─ _textgenmodel_/
    │  ├─ Speaker_2_Name/
    │  │  ├─ _speechgen_/
    │  │  └─ _textgenmodel_/
    │ ...
    └─ @forger.py
```

Finally, from `YourNTS/`,

```shell
$ python3 forger.py
``` 

Repliques are generated one by one, each based on 2 previous ones, and are written into enumerated dirs inside `YourNTS/_repliques_/`. Such dir contains `speaker.txt`, `text.txt`, and `speech.flac`.

After several repliques have been made, the process seems to hang. Actually it does not, only you've reached certain limit, one of

#### Generation parameters

are of two kinds: general and per-speaker. Some of general parameters:

* `REPLIQUES_RESERVE_LEN` (16 by default) prevents filling of disk space with repliques accumulating indefinitely. As soon as the number of repliques in `_repliques_` reaches this limit, the generation is paused. Now choose: either you set it to large value, generate all repliques beforehand (this is how we made the aforementioned demo) and halt the process with Ctrl+C, or open another terminal and from `YourNTS/` run `playeraser.py` (see below).

* `TEXT_LENGTH_MIN` (in tokens, 128 by default)

* `TEXT_LENGTH_MAX` (in tokens, default is 256)

* `LANGUAGE` (`ru`)

* `DEFAULT_TEXT_TEMPERATURE` (1.0)

* `DEFAULT_SPEED` (1.0)

* `DEFAULT_SPEECH_TEMPERATURE` (0.75)

As for per-speaker parameters, provide them in `parameters.json` inside `YourNTS/speakers/SpeakerName/`. Here they are:

* `text_temperature`

* `speed`

* `speech_temperature`

If some parameter is missing or entire `parameters.json` is absent, the general default will be used.

Thus some content has been produced. Now we proceed to

### Playing stage

presents the forged content to the "target auditory". Let countless ways to arrange such "show" bloom in someone else's gardens... we here provide only basic console and web players.

This stage requires neither `speakers` nor `SpeakerName` dirs.

With symlink to `playeraser.py` in `YourNTS/`,

```shell
$ python3 playeraser.py 
```

This script prints and plays repliques from `_repliques_/`, removing each one after it has been played if `DO_ERASE` is `True` (it is by default). If `forger.py` runs in another terminal, it resumes generation... on appropriate hardware, generation occurs faster than playing, so the player always lags approximately `REPLIQUES_RESERVE_LEN` repliques behind the forger, switching to next one immediately, and the amount of used disk space remains bounded from above. (Miceli mentions this supply-overtaking-demand among motivations for "infinite" term.)

`notthatstuff.php` is a browser-oriented alternative. To work as in the demo mentioned above, it needs, in addition to `_repliques_/`, the `portraits` dir with pairs of `.gif` files for each speaker: her/his "talking" animation `SpeakerName_on.gif` and "silent" one `SpeakerName_off.gif`. (We straightforwardly grabbed `.webp` previews from the same YouTube channels (except for one "hybrid" from XIX c.), tinkered with them in [GIMP](https://www.gimp.org/) and exported as `.gif`.) Oh, and `favicon.png`. At server side, where web server with PHP runs (no need for xSQL),

```
.../www/nts/
        ├─ portraits/
        ├─ _repliques_/
        ├─ notthatstuff.php (or index.php)
        └─ favicon.png
```

A lot of possibilities is missed here, unless you start

## Further customisation and improvement

is even more infinite. The scripts are short and generic enough for you to read them all through carefully and get the rest of the details. This (and laziness) is why we have described them above as "black boxes" mostly. Hoping that the code speaks for itself, we encourage you to look into them and shed the light of **your own** comprehension.

One potential way to better quality, among many others, is to take a model trained on much larger and general corpus and *fine-tune* it on the (relatively small and narrow) corpus of given speaker, rather than training it *from scratch* using the latter corpus only. Another hint is to rely on corpora better than YouTube subtitles.

And maybe it's you who will make this mess better than

## marginalia

on the fringes of topicality

all these Python scripts seem brief and simple because they rely on much, much more sophisticated libraries like [Coqui-AI-TTS](https://github.com/idiap/coqui-ai-tts), [transformers](https://github.com/huggingface/transformers), [PyTorch](https://pytorch.org/), [CUDA](https://developer.nvidia.com/cuda-zone), and on models like [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer), and on original content... all made by someone else (to say nothing about hardware: GPU, CPU, ..., down to any resistor and underwater cable), who in turn were "made" by...

this approach regurgitates existing culture, unable to introduce coherent novelty... yet

there are general yet deep principles behind the scene, which show another kind of, in a sense, *simplicity*; only to see it, one has to make certain *effort*, — &ldquo;[μὴ εἶναι βασιλικὴν ἀτραπὸν ...](https://en.wikiquote.org/wiki/Euclid#Attributed)&rdquo;

in the past [a show like this](https://www.jwz.org/dadadodo/dadadodo.cgi) relied on [Markov Chains](https://en.wikipedia.org/wiki/Markov_chain#Markov_text_generators), today it utilises [Generative Pre-Trained Transformers](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer), future may bring Something Else; to understand how any of it works, you need to know *at least* some basic Mathematics, but to *improve* it... welcome to beyond basics

for such controversial projects, can there be any appropriate

## License

is something no one cares about, nevertheless

not &ensp; that &ensp; stuff is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

not &ensp; that &ensp; stuff is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with not &ensp; that &ensp; stuff. If not, see https://www.gnu.org/licenses/.

⚠️ **DEEPFAKEHAZARD** 🤥