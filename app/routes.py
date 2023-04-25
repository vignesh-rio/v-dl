from flask import render_template, redirect, url_for, flash, jsonify
from app import app
from app.forms import DownloadForm
from qtorrent import TorrentClient
import youtube_dl
import os
import requests

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize form
    download_form = DownloadForm()

    # Handle form submission
    if download_form.validate_on_submit():
        # Get video URL from form
        video_url = download_form.url.data

        # Download video and return URL
        video_url = download_video(video_url)

        # Redirect to video download page
        return redirect(url_for('download', video_url=video_url))

    # Render home page
    return render_template('index.html', download_form=download_form)

@app.route('/download/<video_url>', methods=['GET'])
def download(video_url):
    # Render download page
    return render_template('download.html', video_url=video_url)

@app.route('/progress/<video_url>', methods=['GET'])
def progress(video_url):
    # Get progress of video download
    progress = get_download_progress(video_url)

    # Return progress as JSON
    return jsonify(progress)

def download_video(video_url):
    # Create qtorrent client
    client = TorrentClient()

    # Download video using youtube-dl
    with youtube_dl.YoutubeDL({'outtmpl': 'video.mp4'}) as ydl:
        ydl.download([video_url])

    # Add video file to qtorrent client and start download
    torrent = client.add_torrent('video.mp4')
    torrent.start()

    # Get download URL
    download_url = torrent.get_download_url()

    # Return download URL
    return download_url

def get_download_progress(video_url):
    # Check if video file exists
    if not os.path.isfile('video.mp4'):
        return {'progress': 0}

    # Get size of video file
    video_size = os.path.getsize('video.mp4')

    # Get progress of video download from qtorrent client
    client = TorrentClient()
    torrent = client.get_torrent('video.mp4')
    progress = torrent.get_progress()

    # Calculate download progress as a percentage
    download_progress = round(progress / video_size * 100)

    # Return progress as a dictionary
    return {'progress': download_progress}
