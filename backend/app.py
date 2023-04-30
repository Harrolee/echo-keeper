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

PROMPTS_PATH = 'prompts/facts.json'
global_current_project_name = ''


# class Project(object):

#     def __new__(cls):
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(Project, cls).__new__(cls)
#             return cls.instance


def METADATA_JSON_PATH(
    project_name=global_current_project_name): return f'projects/{project_name}/metadata.json'


def CONFIG_JSON_PATH(
    project_name=global_current_project_name): return f'projects/{project_name}/config.json'


@app.route('/projects', methods=['GET'])
def list_projects():
    if request.method == 'GET':
        projects = []
        for path in Path('projects/').iterdir():
            if path.is_dir():
                projects.append(path.name)
    print(projects)
    return projects


@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/load_project', methods=['POST'])
def load_project():
    if request.method == 'POST':
        return


@app.route('/start_project', methods=['POST'])
def start_project():
    if request.method == 'POST':
        global global_current_project_name
        global_current_project_name = request.form['project_name']
        language, model = model_params(
            request.form['language'], request.form['model_size'])
        config = {
            "file_count": 0,
            "language": language,
            "model": model,
            "project_name": global_current_project_name
        }
        failure = init_project(config, global_current_project_name)
        if failure:
            return failure
        return f'Created project at {Path.cwd()}/projects/{global_current_project_name}'


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
        with open(CONFIG_JSON_PATH, 'r') as f:
            config = json.load(f)

        # transcribe audio
        audio_model = whisper.load_model(config['model'])
        result = audio_model.transcribe(save_path, language=config['language'])

        return {"text": result['text'], "filename": save_path}


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
        echo_path = f'wavs/{next_filename()}'
        Path.unlink(Path(echo_path))
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
    with open('wavs/metadata.txt', 'a') as f:
        f.write(f'\n{key}|{value}')


def next_filename():
    with open(CONFIG_JSON_PATH, 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"]}.wav'


def current_filename():
    with open(CONFIG_JSON_PATH, 'r') as f:
        config = json.load(f)
    return f'wav{config["file_count"] - 1}.wav'


def increment_file_count():
    with open(CONFIG_JSON_PATH, 'r') as f:
        config = json.load(f)
    config["file_count"] = config["file_count"] + 1
    with open(CONFIG_JSON_PATH, 'w') as f:
        f.write(json.dumps(config))


def decrement_file_count():
    with open(CONFIG_JSON_PATH, 'r') as f:
        config = json.load(f)
    config["file_count"] = config["file_count"] - 1
    with open(CONFIG_JSON_PATH, 'w') as f:
        f.write(json.dumps(config))


def model_params(language, model_size):
    model = model_size
    # there are no english models for large
    if model_size != 'large' and language == 'english':
        model = model_size + '.en'
    return language, model


def init_project(config, project_name):
    # Ensure the project dir exists
    Path('projects/').mkdir(exist_ok=True)

    try:
        Path(f'projects/{project_name}').mkdir()
    except FileExistsError:
        print(FileExistsError)
        logging.exception(
            f' A project named {project_name} already exists.')
        return

    Path(f'projects/{project_name}/wavs').mkdir()
    with open(CONFIG_JSON_PATH(project_name), 'w') as f:
        f.write(json.dumps(config))
    with open(METADATA_JSON_PATH(project_name), 'w') as f:
        f.write(json.dumps({
            "project_name": f'{project_name}',
            "echoes": [],
        }))


def add_echo(transcription, filename):
    with open(METADATA_JSON_PATH, 'r') as f:
        contents = json.load(f)
    contents['echoes'].append({
        "filename": filename,
        "length_in_seconds": seconds_in_wav(f'wavs/{filename}'),
        "contents": transcription,
    })
    with open(METADATA_JSON_PATH, 'w') as f:
        f.write(json.dumps(contents))


def rm_echo(echo_path):
    rm_echo_from_metadata(echo_path)
    Path.unlink(Path(echo_path))


def rm_echo_from_metadata(filename):
    with open(METADATA_JSON_PATH, 'r') as f:
        metadata = json.load(f)
    metadata['echoes'] = list(
        filter(lambda echo: echo['filename'] != filename, metadata['echoes']))
    with open(METADATA_JSON_PATH, 'w') as f:
        f.write(json.dumps(metadata))


def seconds_in_wav(path_of_wav_file):
    # x = wave.open(path_of_wav_file, 'r')
    # somehow get seconds
    # x.???
    return 3


# def save_wav(audio_file: FileStorage, outfile: str):
    # bytes = audio_file.stream.read()
    # buffer = io.BytesIO(bytes)
    # buffer.seek(0)

    # audio_file.save(buffer)

    # buffer.close()
    # print(audio_file.read())
    # buffer.write(audio_file.read())

    # with wave.open(outfile, 'wb') as out_wav:
    #     # Set the .wav file parameters based on the FileStorage object
    #     out_wav.setnchannels(1)
    #     out_wav.setsampwidth(2)
    #     out_wav.setframerate(44100)

    #     # Write the contents of the buffer to the .wav file
    #     out_wav.writeframes(buffer.read())

    # buffer.close()

    # # Open a new WAV file for writing
    # output_file = wave.open(outfile, 'w')

    # audio_file.sa

    # with open(audio_file, 'rb') as wav_content:
    #     print(wav_content)
    #     # Set WAV file parameters
    #     n_channels = 1  # Mono audio
    #     sample_width = 2  # 16-bit audio
    #     frame_rate = 44100  # Sample rate in Hz
    #     n_frames = len(wav_content)  # Number of frames in the audio data

    #     output_file.setnchannels(n_channels)
    #     output_file.setsampwidth(sample_width)
    #     output_file.setframerate(frame_rate)
    #     output_file.setnframes(n_frames)

    #     # Write the audio data to the WAV file
    #     output_file.writeframesraw(wav_content)

    # # Close the WAV file
    # output_file.close()


@app.route('/export_metadata_txt', methods=['POST'])
def export_metadata_txt(outfile='wavs/metadata.txt'):
    """
    Convert metadata.json to the lj-speech csv format descibed as below by Keith Ito
    excpert below from https://keithito.com/LJ-Speech-Dataset/

        Metadata is provided in transcripts.csv. This file consists of one record per line, delimited by the pipe character (0x7c). The fields are:

        ID: this is the name of the corresponding .wav file
        Transcription: words spoken by the reader (UTF-8)
        Normalized Transcription: transcription with numbers, ordinals, and monetary units expanded into full words (UTF-8).
    """
    if request.method == 'POST':
        with open(outfile, 'w') as f:
            pass
        with open(METADATA_JSON_PATH, 'r') as f:
            metadata = json.load(f)
        for echo in metadata['echoes']:
            add_line(echo['filename'], echo['contents'])
        return 'exported'


@app.route('/duration_total', methods=['GET'])
def duration_total():
    if request.method == 'GET':
        total_duration = 0
        with open(METADATA_JSON_PATH, 'r') as f:
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
