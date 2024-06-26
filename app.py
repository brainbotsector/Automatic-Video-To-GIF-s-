from flask import Flask, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
import subprocess
import speech_recognition as sr
import logging
import yt_dlp
import wave
import contextlib
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_video():
    youtube_url = request.form.get('youtube_url')
    if 'file' not in request.files and not youtube_url:
        return 'No file part or YouTube URL provided'
    if youtube_url:
        video_path = download_youtube_video(youtube_url)
    else:
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)

    process_video(video_path)
    return render_template('success.html', filenames=os.listdir(app.config['OUTPUT_FOLDER']))

def download_youtube_video(youtube_url, output_folder='downloads'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        video_path = ydl.prepare_filename(info_dict)
        return video_path

def process_video(video_path):
    audio_path = convert_video_to_audio(video_path)
    transcription, segments = transcribe_audio(audio_path)
    segment_and_create_gifs(video_path, segments)

def convert_video_to_audio(video_path):
    audio_path = os.path.splitext(video_path)[0] + '.wav'
    try:
        subprocess.run(['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting video to audio: {e}")
    return audio_path

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    transcription = ""
    segments = []

    with contextlib.closing(wave.open(audio_path, 'r')) as wf:
        duration = wf.getnframes() / float(wf.getframerate())
        chunk_size = 15  # Split audio into 15-second chunks (adjust as needed)
        for start in range(0, int(duration), chunk_size):
            end = min(start + chunk_size, int(duration))
            retries = 3  # Number of retries
            while retries > 0:
                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source, offset=start, duration=(end - start))
                try:
                    chunk_transcription = recognizer.recognize_google(audio)
                    transcription += chunk_transcription + " "
                    segments.extend(generate_segments(chunk_transcription, start))
                    break  # Exit retry loop on successful recognition
                except sr.RequestError as e:
                    logging.error(f"Request error: {e}")
                    break  # Exit retry loop on request error
                except sr.UnknownValueError:
                    logging.error("Could not understand audio, retrying...")
                    retries -= 1
                    continue  # Retry recognition

    return transcription, segments




def generate_segments(transcription, offset):
    words = transcription.split()
    segments = []
    start = offset
    duration = 3  # Duration for each segment in seconds
    words_per_segment = 5  # Number of words per segment

    for i in range(0, len(words), words_per_segment):
        end = start + duration
        segment_text = ' '.join(words[i:i + words_per_segment])
        segments.append({'start': start, 'end': end, 'text': segment_text})
        start = end

    return segments

def segment_and_create_gifs(video_path, segments):
    for i, segment in enumerate(segments):
        start = segment['start']
        end = segment['end']
        output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], f"segment_{uuid.uuid4().hex}.mp4")
        gif_path = os.path.join(app.config['OUTPUT_FOLDER'], f"segment_{uuid.uuid4().hex}.gif")
        subtitle_text = segment['text']

        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path, '-ss', str(start), '-to', str(end),
                '-vf', f"drawtext=text='{subtitle_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h-50",
                '-c:a', 'copy', output_video_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating video segment {i}: {e}")
            continue

        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', output_video_path, '-vf', 'fps=10,scale=320:-1:flags=lanczos,palettegen', 'palette.png'
            ], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error generating palette for segment {i}: {e}")
            continue

        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', output_video_path, '-i', 'palette.png', '-filter_complex', 'fps=10,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse', gif_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating GIF for segment {i}: {e}")
            continue

        os.remove(output_video_path)

@app.route('/output/<filename>')
def send_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)




