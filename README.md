---
id: VOSK_STT
label: VOSK STT
title: VOSK STT - Speech to Text
type: stts
description: "Allows Naomi to use VOSK for active listening"
source: https://github.com/aaronchantrill/Naomi_VOSK_STT/blob/main/README.md
meta:
  - property: og:title
    content: "VOSK STT - Speech to Text"
  - property: og:description
    content: "Allows Naomi to use VOSK for active listening"
---

# VOSK STT - Speech to Text

This plugin allows [Naomi](https://projectnaomi.com/) to use [VOSK](https://alphacephei.com/vosk/)
to convert speech to text. This plugin does not currently do language model
adaptation automatically, but it is already very good, at least in English, so
it may not be necessary for you to adapt the language model if it already knows
all the words needed.

Instructions for adapting the language model are at https://alphacephei.com/vosk/lm
but I'll also summarize them here:

1. Install Kaldi (https://kaldi-asr.org). Kaldi claims to require Python 2.7, or at least it did the last time I installed it. If you don't want to install Python 2.7 on your system, you can edit the tools/extras/check_dependencies.sh script and comment out or remove the parts about Python 2.7 around lines 96 and 111, then create a python directory and a file called .use_default_python. As far as I can tell, Kaldi does not actually need Python 2.7.
2. Naomi setup has already installed Phonetisaurus into your Naomi virtual environment, so just download and install SRILM from http://www.speech.sri.com/projects/srilm/. You will have to register with SRI and tell them you are not using it for commercial purposes. I download it, saving it to a file named tools/srilm.tgz. Then I modify the tools/extras/install_srilm.sh script and comment out the block starting on line 19 with `if [ ! -f srilm.tgz ] && [ ! -f srilm.tar.gz ] && [ ! -d srilm ]; then` which tries to download the file for you. If you are installing on a Raspberry Pi 5, then you will also need to modify the SRILM installer to allow it to compile on aarch64 systems as detailed at https://github.com/G10DRAS/SRILM-on-RaspberryPi.
3. Download the appropriate VOSK _compile archive depending on your chosen language:
  - English - https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-compile.zip
  - French - https://alphacephei.com/vosk/models/vosk-model-fr-0.6-linto-2.2.0-compile.zip
  - German - https://alphacephei.com/vosk/models/vosk-model-de-0.21-compile.zip
4. Unzip the archive and update path.sh to point to KALDI_ROOT (if kaldi is installed in your home directory, ie. ~/kaldi, then path.sh should be correct already). The folder you unzip the archive to will be referred to as $VOSK_COMPILE below.
5. Copy your extra.txt file from ~/.config/naomi/vocabularies/&lt;locale&gt;/VOSK STT/&lt;vocabulary&gt;/extra.txt
to $VOSK_COMPILE/db/extra.txt.
6. Activate your Naomi virtual environment by running `workon Naomi`.
7. Run $VOSK_COMPILE/compile-graph.sh.
8. Copy your updated graph from $VOSK_COMPILE/exp/chain/tdnn/graph to ~/.config/naomi/vosk/vosk-model-&lt;locale&gt;-&lt;version&gt;/graph.

If you are interested in helping figure out how to build a custom HCLG.fst
file using OpenGRM or even KenLM instead of SRILM, or knows about static vs
dynamic graphs or how to manipulate ARPA language models, I'd love to hear from
you.

To activate this plugin, change your profile.yml file to set the active and/or
special listener engines and point VOSK to its like this:

```
active_stt:
  engine: VOSK STT
```

This plugin will download and unzip an appropriate model based on your selected
language/locale to ~/.config/naomi/vosk.

```
VOSK STT:
  model: /home/naomi/.config/naomi/vosk/vosk-model-en-us-0.22
```

Special thanks to @Akul2010 for submitting an early version of this plugin.
<EditPageLink/>
