import os
from pathlib import Path
import json
import tempfile
import flask
import logging
from flask import request, send_from_directory
from flask_cors import CORS
import whisper

app = flask.Flask(__name__, static_url_path='', static_folder='build')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ECHO_SCHEMA = {
    "filename": 'name',
    'length_in_seconds': 22,
    'contents': 'words transcribed by user',
}

PROMPTS_PATH = Path('user/prompts/prompts.json')
PROJECTS_PATH = Path('user/projects')


class Project():
    """
    Singleton class for managing pathnames
    """

    def __init__(self):
        self._name = ""

    def name(self):
        return self._name

    def set_name(self, project_name: str):
        self._name = project_name.replace(' ', '')

    def project_path(self):
        return Path(PROJECTS_PATH, self._name)

    def metadata_path(self):
        return Path(self.project_path(), 'metadata.json')

    def config_path(self):
        return Path(self.project_path(), 'config.json')

    def wavs_path(self):
        return Path(self.project_path(), 'wavs')

    def export_path(self):
        return Path(self.project_path(), 'metadata.txt')


project = Project()


@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/projects', methods=['GET'])
def list_projects():
    if request.method == 'GET':
        projects = []
        for path in PROJECTS_PATH.iterdir():
            if path.is_dir():
                projects.append(path.name)
    return projects


@app.route('/load_project', methods=['POST'])
def load_project():
    if request.method == 'POST':
        project.set_name(request.form['project_name'])
        # language, model = ogre(project.name())
        # # overwrite config with new language and model_size
        # language, model = model_params(
        #     request.form['language'], request.form['model_size'])
        return f"Loaded {project.name()}"


@app.route('/start_project', methods=['POST'])
def start_project():
    if request.method == 'POST':
        project.set_name(request.form['project_name'])
        language, model = model_params(
            request.form['language'], request.form['model_size'])
        config = {
            "file_count": 0,
            "language": language,
            "model": model,
            "project_name": project.name()
        }
        failure = init_project(config)
        if failure:
            return failure
        return f'Created project at {Path.cwd()}/projects/{project.name()}'


@app.route('/save_audio', methods=['POST'])
def save_audio():
    if request.method == 'POST':
        wav_file = request.files['audio_data']
        save_path = Path(project.wavs_path(), next_filename()).__str__()
        wav_file.save(save_path)
        # retrieve model and language from config
        with open(project.config_path(), 'r') as f:
            config = json.load(f)
        # transcribe audio
        audio_model = whisper.load_model(config['model'])
        result = audio_model.transcribe(save_path, language=config['language'])
        return {"text": result['text'].strip(), "filename": save_path}


@app.route('/save_transcription', methods=['POST'])
def save_transcription():
    if request.method == 'POST':
        transcription = request.form['reviewedTranscription']
        add_echo(transcription, f'{next_filename()}')
        increment_file_count()
        return f'saved {transcription}'


@app.route('/delete_recording', methods=['DELETE'])
def delete_recording():
    if request.method == 'DELETE':
        echo_path = Path(project.wavs_path(), next_filename())
        Path.unlink(echo_path)
        return f'deleted {echo_path}'


@app.route('/delete_echo', methods=['DELETE'])
def delete_echo():
    # deletes the latest echo from fs and from metadata['echoes']
    echo_path = f'wavs/{current_filename()}'
    rm_echo(echo_path)
    decrement_file_count()


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


def add_line(key: str, value: str):
    with open(project.export_path(), 'a') as f:
        f.write(f'\n{key}|{value}|{value}')
        # TODO: Actually export the third column to Keith Ito's ljspeech spec
        # instead of lazily appending the same value to the end


def next_filename():
    with open(project.config_path(), 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"]}.wav'


def current_filename():
    with open(project.config_path(), 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"] - 1}.wav'


def increment_file_count():
    with open(project.config_path(), 'r') as f:
        config = json.load(f)
    config["file_count"] = config["file_count"] + 1
    with open(project.config_path(), 'w') as f:
        f.write(json.dumps(config))


def decrement_file_count():
    with open(project.config_path(), 'r') as f:
        config = json.load(f)
    config["file_count"] = config["file_count"] - 1
    with open(project.config_path(), 'w') as f:
        f.write(json.dumps(config))


def model_params(language, model_size):
    model = model_size
    # there are no english models for large
    if model_size != 'large' and language == 'english':
        model = model_size + '.en'
    return language, model


def init_project(config):
    # Ensure the project dir exists
    Path('user/projects/').mkdir(exist_ok=True)

    try:
        Path(project.project_path()).mkdir()
    except FileExistsError:
        print(FileExistsError)
        logging.exception(
            f' A project named {project.name()} already exists.')
        return

    Path(project.wavs_path()).mkdir()
    with open(project.config_path(), 'w') as f:
        f.write(json.dumps(config))
    with open(project.metadata_path(), 'w') as f:
        f.write(json.dumps({
            "project_name": project.name(),
            "echoes": [],
        }))


def add_echo(transcription, filename):
    with open(project.metadata_path(), 'r') as f:
        contents = json.load(f)
    contents['echoes'].append({
        "filename": filename,
        "length_in_seconds": seconds_in_wav(f'wavs/{filename}'),
        "contents": transcription,
    })
    with open(project.metadata_path(), 'w') as f:
        f.write(json.dumps(contents))


def rm_echo(echo_path):
    rm_echo_from_metadata(echo_path)
    Path.unlink(Path(echo_path))


def rm_echo_from_metadata(filename):
    with open(project.metadata_path(), 'r') as f:
        metadata = json.load(f)
    metadata['echoes'] = list(
        filter(lambda echo: echo['filename'] != filename, metadata['echoes']))
    with open(project.metadata_path(), 'w') as f:
        f.write(json.dumps(metadata))


def seconds_in_wav(path_of_wav_file):
    # x = wave.open(path_of_wav_file, 'r')
    # TODO: somehow get seconds
    # x.???
    return 3


@app.route('/export_metadata_txt', methods=['POST'])
def export_metadata_txt():
    """
    Convert metadata.json to the lj-speech csv format descibed as below by Keith Ito
    exert below from https://keithito.com/LJ-Speech-Dataset/

        Metadata is provided in transcripts.csv. This file consists of one record per line, delimited by the pipe character (0x7c). The fields are:

        ID: this is the name of the corresponding .wav file
        Transcription: words spoken by the reader (UTF-8)
        Normalized Transcription: transcription with numbers, ordinals, and monetary units expanded into full words (UTF-8).
    """
    if request.method == 'POST':
        with open(project.metadata_path(), 'r') as f:
            metadata = json.load(f)
        for echo in metadata['echoes']:
            add_line(echo['filename'], echo['contents'])
        return 'exported'


@app.route('/duration_total', methods=['GET'])
def duration_total():
    if request.method == 'GET':
        total_duration = 0
        with open(project.metadata_path(), 'r') as f:
            metadata = json.load(f)
        for echo in metadata['echoes']:
            total_duration += echo['length_in_seconds']
        return f'recorded {total_duration} seconds of audio for this project'


@app.route('/prompts', methods=['GET'])
def get_prompts():
    if request.method == 'GET':
        with open(PROMPTS_PATH, 'r') as f:
            data = json.load(f)
            assert len(data['prompts']) != 0
        return {'prompts': data['prompts']}
