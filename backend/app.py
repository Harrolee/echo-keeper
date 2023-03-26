import os
import pathlib
import json
import tempfile
import flask
from flask import request
from flask_cors import CORS
import whisper

app = flask.Flask(__name__)
CORS(app)


@app.route('/load_project', methods=['POST'])
def load_project():
    if request.method == 'POST':
        return

@app.route('/start_project', methods=['POST'])
def start_project():
    if request.method == 'POST':
        language, model = model_params(request.form['language'], request.form['model_size'])
        config = {
            "file_count": 0,
            "language": language,
            "model": model
        }
        init_project(config)
        return f'Created project at {pathlib.Path.cwd()}/wavs'


@app.route('/save_audio', methods=['POST'])
def save_audio():
    if request.method == 'POST':

        wav_file = request.files['audio_data']
        try:
            save_path = f'wavs/{next_filename()}'
            wav_file.save(save_path)
        except:
            start_project()
            save_path = f'wavs/{next_filename()}'
            wav_file.save(save_path)
        
        # retrieve model and language from config
        with open('wavs/config.json','r') as f:
            config = json.load(f)

        # transcribe audio
        audio_model = whisper.load_model(config['model'])
        result = audio_model.transcribe(save_path, language=config['language'])

        # write transcribed line to metadata.txt
        add_line(result['text'], save_path)
        iterate_file_count()

        return {"text": result['text'], "filename": save_path} 


@app.route('/save_transcription', methods=['POST'])
def save_transcription():
    if request.method == 'POST':
        transcription = request.form['reviewedTranscription']
        print(transcription)
        return 'success'


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if request.method == 'POST':
        language = request.form['language']
        model = request.form['model_size']

        # there are no english models for large
        if model != 'large' and language == 'english':
            model = model + '.en'
        audio_model = whisper.load_model(model)
            
        temp_dir = tempfile.mkdtemp()
        save_path = os.path.join(temp_dir, 'temp.wav')

        wav_file = request.files['audio_data']
        wav_file.save(save_path)

        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        return result['text']
    else:
        return "This endpoint only processes POST wav blob"
        

def add_line(text, filename): 
    with open('wavs/metadata.txt', 'a') as f:
        f.write(f'\n{filename}|{text}')


def next_filename():
    with open('wavs/config.json', 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"]}'

def iterate_file_count():
    with open('wavs/config.json', 'r') as f:
        config = json.load(f)
    config["file_count"] = config["file_count"] + 1;
    with open('wavs/config.json', 'w') as f:
        f.write(json.dumps(config))


def model_params(language, model_size):
    model = model_size
    # there are no english models for large
    if model_size != 'large' and language == 'english':
        model = model_size + '.en'
    return language, model

def init_project(config):
    try:
        pathlib.Path('wavs').mkdir(exist_ok=False)
    except FileExistsError:
        return 'Project already exists. This version supports only one project.'
    except:
        return 'Some other error'

    with open('wavs/config.json', 'w') as f:
        f.write(json.dumps(config))
    
    with open('wavs/metadata.txt', 'w') as f:
        pass