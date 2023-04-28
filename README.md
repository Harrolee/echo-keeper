<p align="center">
  <img width="60px" src="https://user-images.githubusercontent.com/6180201/124313197-cc93f200-db70-11eb-864a-fc65765fc038.png" alt="giant microphone"/>   <br/>
  <h2 align="center">Echo Keeper</h2>
  <h6 align="center">Create your own datasets for speech synthesis</h6>
</div>

# What

Create voice datasets in the lj-speech format.
Export your dataset and use it to finetune a model with [Coqui🐸 TTS](https://github.com/coqui-ai/TTS)

# Setup

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

# License

This repository and the code and model weights of Whisper are released under the MIT License.
