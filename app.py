import os
import redis

from flask import Flask

app = Flask(__name__)

r = None


@app.route("/")
def hello_world():
    return "hey there world"


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
    r = redis.Redis(host=os.environ.get('REDIS_URL'), port=6379, db=1)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
