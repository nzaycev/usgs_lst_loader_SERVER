import os
import time
from threading import Thread

import requests, rfc6266
from flask import Flask, request
from flask_cors import cross_origin
from usgs_test import searchScenes, downloadScene, checkScenes
from main import calcAllLST
from flask_socketio import SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
emit = socketio.emit
socketio.init_app(app, cors_allowed_origins="*")

# TODO: write to file
# fresh_date = checkScenes()['results'][0]['temporalCoverage']['endDate']
# fresh_date_updated = time.time()
fresh_date = None
fresh_date_updated = None


@app.route('/')
@cross_origin()
def hello_world():
    return {"Hello": 'world'}


@app.route('/search_scenes', methods=["POST"])
@cross_origin()
def search_scenes():
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    spatial = request.json.get('spatial')
    return searchScenes(start_date, end_date, spatial)


def download_file(url, displayId):
    local_filename = './' + displayId
    # NOTE the stream=True parameter below
    # print(requests.head(url, stream=True))
    # return

    from os.path import expanduser
    CHUNK_SIZE = 4 * 1024 * 1024
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        size=r.headers['Content-length']
        filename=rfc6266.parse_headers(r.headers["Content-Disposition"]).filename_unsafe
        downloaded_filename = '{}/USGS_Loader/layers/{}/{}'.format(expanduser('~').replace('\\\\', '/'), displayId, filename)

        print('size', size)
        print('filename', filename)
        emit("set_download_state", {
            'fileSize': size,
            'fileName': filename,
            'downloadedSize': 0
        })
        if os.path.isfile(downloaded_filename):
            print('sizes', size, os.path.getsize(downloaded_filename))
            if os.path.getsize(downloaded_filename) == int(size):
                r.close()
                emit("set_download_state", {
                    'downloadedSize': size
                })
                return
            else:
                os.remove(downloaded_filename)

        k = 0

        with open('{}/USGS_Loader/layers/{}/{}'.format(expanduser('~').replace('\\\\', '/'), displayId, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                k = k + 1
                print('chunk', k, k * CHUNK_SIZE)
                emit("set_download_state", {
                    'downloadedSize': k * CHUNK_SIZE
                })
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return local_filename

@app.route('/get_date_bounds')
@cross_origin()
def get_date_bounds():
    global fresh_date
    global fresh_date_updated
    if fresh_date is not None:
        if fresh_date_updated > time.time() + 1000 * 60 * 30:
            pass
        else:
            return fresh_date
    fresh_date = checkScenes()['results'][0]['temporalCoverage']['endDate']
    fresh_date_updated = time.time()
    return fresh_date

@app.route('/download_scene')
@cross_origin()
def download_scene():
    entity_id = request.args.get('entityId')
    display_id = request.args.get('displayId')
    # return download_file()
    # return downloadScene(entity_id)

    # for i in ['{home}/USGS_Loader', '']
    try:
        os.mkdir('{}/USGS_Loader'.format(os.path.expanduser('~').replace('\\\\', '/')))
    except Exception as e:
        print(e)

    try:
        os.mkdir('{}/USGS_Loader/layers'.format(os.path.expanduser('~').replace('\\\\', '/')))
    except Exception as e:
        print(e)

    try:
        os.mkdir('{}/USGS_Loader/out'.format(os.path.expanduser('~').replace('\\\\', '/')))
    except Exception as e:
        print(e)

    try:
        os.mkdir('{}/USGS_Loader/layers/{}'.format(os.path.expanduser('~').replace('\\\\', '/'), display_id))
    except Exception as e:
        print(e)

    try:
        os.mkdir('{}/USGS_Loader/out/{}'.format(os.path.expanduser('~').replace('\\\\', '/'), display_id))
    except Exception as e:
        print(e)

    def _emit(data):
        print('emiting')
        emit("set_download_state", data)


    def donwload_task(entity_id, display_id):
        ds = downloadScene(entity_id)
        print('ds', ds)
        downloads = ds['preparingDownloads'] + ds['availableDownloads']


        l = 0
        for d in downloads:
            l = l + 1
            url = d['url']
            emit("set_download_state", {'step': 'DOWNLOADING', 'fileCount': l})
            download_file(url, display_id)

        emit("set_download_state", {'step': 'CALCULATING'})

        calcAllLST('{}/USGS_Loader/layers/{}'.format(os.path.expanduser('~').replace('\\\\', '/'), display_id), _emit)
        emit("set_download_state", {'step': 'READY', 'fileName': 'out/' + display_id})

    thread = Thread(target=donwload_task, kwargs={'entity_id': entity_id, 'display_id': display_id})
    thread.start()

    return {'path': 'out/' + display_id}

if __name__ == '__main__':
    socketio.run(app, debug=True)