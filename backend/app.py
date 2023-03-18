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
        # make config file
        with open('wavs/config.txt', 'w') as f:
            f.write(json.dumps(config))
        
        with open('wavs/metadata.txt', 'w') as f:
            f.write('empty')

        return f'Created project at {pathlib.Path.cwd()}/wavs'


@app.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        language = request.form['language']
        model = request.form['model_size']

        # there are no english models for large
        if model != 'large' and language == 'english':
            model = model + '.en'
        audio_model = whisper.load_model(model)

        wav_file = request.files['audio_data']
        save_path = f'wavs/{next_file_name()}'
        wav_file.save(save_path)

        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        return {"text": result['text'], "filename": save_path} 


@app.route('/updateTranscription', methods=['PUT'])
def updateTranscription():
    if request.method == 'PUT':
        # get filename from request
        # get new text from request
        # use filename to find line to update
        # replace old text in that line with new text
        return


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
        f.write(f'{filename}|{text}')


def next_file_name():
    with open('wavs/config.txt', 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"]}'