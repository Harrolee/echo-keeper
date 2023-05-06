<p align="center">
  <img width="60px" src="https://user-images.githubusercontent.com/6180201/124313197-cc93f200-db70-11eb-864a-fc65765fc038.png" alt="giant microphone"/>   <br/>
  <h2 align="center">Echo Keeper</h2>
  <h6 align="center">Create your own datasets for training speech synthesis models</h6>
</div>

# What

Create voice datasets in the lj-speech format.(1)
Export your dataset and use it to train a model with [Coqui 🐸 TTS](https://github.com/coqui-ai/TTS)

# Quickstart 1: Just record and transcribe audio

## Run container

Choose the directory where you would like to retrieve your exported dataset.
Bind mount that directory to `/app/backend/user/projects` with (-v) the volume option as below

`docker run -p 8000:8000 -v /path/to/your/export/dir:/app/backend/user/projects echokeeper`

## Default prompts?

Running the container this way loads [these prompts](https://github.com/Harrolee/echo-keeper/tree/main/backend/user/prompts). You could record a 25minute dataset using these. The result will probably not fit your use case. I recommend building your own prompts with [this notebook](https://colab.research.google.com/drive/1lCEgck32s_Jbqo9ZLxfa92Djp1kLx2or?usp=sharing).

# Quickstart 2: Bring your own prompts

_If you want to use your own prompts..._

## Run container

1. Choose the directory where you would like to retrieve your exported dataset. In this example, we'll call that directory 'output'.
2. Create a directory structure like this:

```
  /output
  |-/projects
    |--leave this dir empty if you are starting from scratch
    |--if you want to continue recording to a project, place that project folder here
  |-/prompts
    |--prompt.json
```

3. Bind mount your output dir to the `/app/backend/user`
   `docker run -p 8000:8000 -v /path/to/your/export/dir:/app/backend/user echokeeper`

# Use

## Create a new project

Type a name for your project into the New Project input

## Select model parameters for Whisper

[Whisper](https://github.com/openai/whisper) is the magic behind this whole app. It transcribes your recorded audio into text
Select your language and model size. The bigger models perform better but require more RAM and disk space.

## Read a prompt and record audio

The model will be downloaded after you make your first recording. Unfortunately, this means there will be a longish pause between the moment that you finish your first recording and the moment that you see your first transcription. Every following transcription will feel instantaneous.

# Manual Setup

_run on your machine without a container_

1. Whisper requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) and [`portaudio`](http://portaudio.com/docs/v19-doxydocs/index.html) to be installed on your system, which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg
sudo apt install portaudio19-dev

# on Arch Linux
sudo pacman -S ffmpeg
sudo pacman -S portaudio

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg
brew install portaudio

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

3. Install the backend and frontend environmet `sh install_playground.sh`
4. Run the backend `cd backend && source venv/bin/activate && flask run --port 8000`
5. In a different terminal, run the React frontend `cd interface && yarn start`

# Work in Progress

- [] Normalize dataset audio during the Export phase
- [] Track duration of recordings
- [] In export_metadata_txt(), create the third column of the ljspeech format, per Keith Ito's spec

# License

This repository and the code and model weights of Whisper are released under the MIT License.

# Footnotes

(1) https://keithito.com/LJ-Speech-Dataset/
Metadata is provided in transcripts.csv. This file consists of one record per line, delimited by the pipe character (0x7c). The fields are:

    ID: this is the name of the corresponding .wav file
    Transcription: words spoken by the reader (UTF-8)
    Normalized Transcription: transcription with numbers, ordinals, and monetary units expanded into full words (UTF-8).

!Note: Normalized Transcriptions aren't complete as of 5/6/23
