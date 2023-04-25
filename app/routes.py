import os
import time
import shutil
import urllib.parse
import youtube_dl
import m3u8
from flask import Flask, render_template, request, jsonify, current_app, url_for
from aria2p.client import DownloadInput

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    path = os.path.join(current_app.config['DOWNLOAD_PATH'], 'video.mp4')
    try:
        if 'youtube.com' in url:
            ydl_opts = {'outtmpl': path}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            # Connect to the Aria2 client
            aria2_client = Client(
                host="http://localhost",
                port=6800,
                secret="",
            )

            # Add the URL to the client
            download = aria2_client.add(DownloadInput(url))

            # Wait for the download to finish
            while download.is_active:
                time.sleep(1)

            # Move the downloaded video to the download path
            filename = os.path.basename(download.files[0].path)
            src_path = download.files[0].path
            dest_path = os.path.join(current_app.config['DOWNLOAD_PATH'], filename)
            shutil.move(src_path, dest_path)

        # Return the URL where the downloaded video can be accessed
        url = url_for('static', filename=f'downloads/{filename}')
        return jsonify({'status': 'success', 'url': url})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download-m3u8', methods=['POST'])
def download_m3u8():
    url = request.form['url']
    path = os.path.join(current_app.config['DOWNLOAD_PATH'], 'video.mp4')
    try:
        playlist = m3u8.load(url)
        segments = [urllib.parse.urljoin(url, segment.uri) for segment in playlist.segments]

        with open(path, 'wb') as f:
            for segment_url in segments:
                segment_data = urllib.request.urlopen(segment_url).read()
                f.write(segment_data)

        # Return the URL where the downloaded video can be accessed
        url = url_for('static', filename='downloads/video.mp4')
        return jsonify({'status': 'success', 'url': url})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete', methods=['POST'])
def delete():
    path = os.path.join(current_app.config['DOWNLOAD_PATH'], 'video.mp4')
    try:
        if os.path.exists(path):
            os.remove(path)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'File not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
