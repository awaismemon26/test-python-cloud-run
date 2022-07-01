from google.api_core.exceptions import NotFound
from logging import Logger
import os
import redis
from google.cloud import storage
from flask import Flask, render_template

from flask import Flask
import logging
from logging.config import fileConfig

fileConfig('logger.cfg')
LOGGER = logging.getLogger()

if 'LOG_LEVEL' in os.environ:
    log_levels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20,
                  'WARN': 30, 'ERROR': 40, 'CRITICAL': 50}
    if os.environ.get('LOG_LEVEL') in log_levels:
        LOGGER.setLevel(log_levels[os.environ.get('LOG_LEVEL')])
    else:
        LOGGER.error(
            f'LOG_LEVEL {os.environ.get("LOG_LEVEL")} is not a valid level. using {LOGGER.level}')
else:
    LOGGER.warning(f'LOG_LEVEL not set. current log level is {LOGGER.level}')


app = Flask(__name__)

r = None


@app.route("/download/<value>")
def download_file(value):
    download_from_bucket("test-python-001", f"{value}.jpeg")
    if os.path.isfile(f"{value}.jpeg"):
        return render_template("hello.html", value=f"{value}.jpeg"), 200
    return "NotFound", 404


def download_from_bucket(bucket_name, file_name, folder_path=None):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        full_path = os.path.join(
            folder_path, file_name) if folder_path else file_name
        blob = bucket.blob(full_path)
        blob.download_to_filename(file_name)
    except NotFound as e:
        Logger.error(f'file {full_path} not found in bucket {bucket_name}')
        Logger.error(e)


@app.route("/")
def hello_world():
    global r
    r = redis.Redis(host=os.environ.get('REDIS_URL'), port=6379, db=1)
    return "Init redis"


@app.route('/add/<key>/<value>')
def add(key, value):
    global r
    if r is None:
        return 'cache not initialised', 500
    r.set(key, value)
    return f'Added {key}:{value} to the cache', 201


@app.route('/delete/<key>')
def delete(key):
    global r
    if r is None:
        return 'cache not initialised', 500
    r.delete(key)
    return f'Deleted {key}from the cache', 200


@app.route('/get/<key>')
def get(key):
    global r
    if r is None:
        return 'cache not initialised', 500
    value = r.get(key)
    return f'Got the value "{value}" for the key "{key}" from the cache', 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
