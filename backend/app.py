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
        # make wavs dir
        try:
            pathlib.Path('wavs').mkdir(exist_ok=False)
        except FileExistsError:
            return 'Project already exists. This version supports only one project.'
        except:
            return 'Some other error'

        config = {
            "file_count": 0
        }
        with open('wavs/config.json', 'w') as f:
            f.write(json.dumps(config))
        
        with open('wavs/metadata.txt', 'w') as f:
            pass

        return f'Created project at {pathlib.Path.cwd()}/wavs'


@app.route('/save', methods=['POST'])
def save_audio():
    if request.method == 'POST':
        language = request.form['language']
        model = request.form['model_size']

        # there are no english models for large
        if model != 'large' and language == 'english':
            model = model + '.en'
        audio_model = whisper.load_model(model)

        wav_file = request.files['audio_data']
        save_path = f'wavs/{next_filename()}'
        wav_file.save(save_path)
        

        # edit transcription

        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        # write transcribed line to metadata.txt
        add_line(result['text'], save_path)
        iterate_file_count()

        return {"text": result['text'], "filename": save_path} 


# @app.route('/save_transcription', methods=['PUT'])
# def save_transcription():
#     if request.method == 'PUT':
#         transcription = request.form['transcription']




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