import os
import time
import shutil
import urllib.parse
import youtube_dl
import m3u8
import qbittorrentapi
from flask import Flask, render_template, request, jsonify, current_app, url_for

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
            # Connect to the qBittorrent client
            qbt_client = qbittorrentapi.Client(host='localhost', port=8080)
            qbt_client.login('admin', 'adminadmin')

            # Add the magnet URL to the client
            qbt_client.torrents_add(urls=url)

            # Wait for the torrent to finish downloading
            while not any(t.progress == 1.0 for t in qbt_client.torrents_info()):
                time.sleep(1)

            # Save the downloaded video to the download path
            for torrent in qbt_client.torrents_info():
                if torrent.name.endswith('.mp4'):
                    with open(path, 'wb') as f:
                        f.write(qbt_client.torrents_files(torrent.hash)[0].content)

        # Return the URL where the downloaded video can be accessed
        url = url_for('static', filename='downloads/video.mp4')
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
