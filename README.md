# Automatic-Video-To-GIFs
# Video to GIF Converter

This project converts uploaded video files or YouTube video URLs into GIFs with subtitles based on transcribed audio. The application is built using Flask, FFmpeg, and Google's Speech Recognition API.

# Features

Upload video files or provide YouTube URLs to convert.

Automatically converts videos to audio, transcribes the audio, and generates GIFs with subtitles.

Provides a web interface for uploading videos and viewing the generated GIFs.

# Installation

Python 3.6+

FFmpeg

Pip

# Step-by-Step Guide

Clone the repository

-- git clone https://github.com/yourusername/videotogif.git

-- cd videotogif

-- Install FFmpeg

## Windows: Download the FFmpeg executable from the FFmpeg website and add it to your system PATH.

## macOS: Use Homebrew to install FFmpeg:

brew install ffmpeg

## Linux: Use your package manager to install FFmpeg. For example, on Debian-based systems:

sudo apt-get install ffmpeg

## Install required Python packages

Create and activate a virtual environment:

-- python -m venv venv

-- source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

## Install the dependencies:

-- pip install -r requirements.txt

# Usage

1 - Run the Flask app
  
    - python app.py
    
2 - Open the web interface

    - Navigate to http://127.0.0.1:5000 in your web browser. You should see a form for uploading video files or providing YouTube URLs.
    
3 - Upload a video file or paste a YouTube URL

    - To upload a video file, choose a file from your local system.
    
    - To use a YouTube URL, paste the URL in the provided input field.
    
4 - Submit the form

5 - Click on the "Upload / Convert" button to start the conversion process. A loading spinner will indicate that the GIFs are being created.

6 - View the generated GIFs
    - After the conversion process is complete, you will be redirected to a page displaying the generated GIFs. You can click on the GIFs to download them.
