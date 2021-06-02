from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_file
from flask import url_for
import instaloader
import configparser
import os

from werkzeug.utils import redirect

parser = configparser.ConfigParser()
parser.read('autobot.config')

AUTBOT_HOST = parser.get('autobot', 'host')
AUTBOT_PORT = parser.get('autobot', 'port')

POST_PREFIX = parser.get('post', 'prefix')

EXTENSION_IMAGE = parser.get('extension', 'image')
EXTENSION_VIDEO = parser.get('extension', 'video')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/post/<target>/<filename>', methods=['GET'])
def get(target, filename):
    return send_file(os.path.join(target, filename))

@app.route('/post', methods=['POST'])
def post():
    username = request.form['username']
    password = request.form['password']

    caption = request.form['caption']

    id = request.form['url'].rstrip('/').split('/')[-1]
    target = '%s%s' % (POST_PREFIX, id)

    post = request.form.get('post')
    download = request.form.get('download')

    try:
        filename = download_post(username, password, id, target)

        if not download == None:
            return redirect(url_for('.get', target=target, filename=filename))

        if not post == None:
            return jsonify({
                'message': 'This operation is currently not supported'
            }), 200

        return jsonify({
            'message': 'Unknown operation'
        }), 400
    except instaloader.exceptions.BadCredentialsException:
        return jsonify({
            'message': 'Authentication error'
        }), 400
    except instaloader.exceptions.BadResponseException:
        return jsonify({
            'message': 'Probably wrong id'
        }), 400
    except Exception as exception:
        print(exception)
        return jsonify({
            'message': 'Something went wrong'
        }), 500
    


def download_post(username, password, id, target):
    L = instaloader.Instaloader()
    L.login(username, password)

    post = instaloader.structures.Post.from_shortcode(L.context, id)
    L.download_post(post, target=target)

    extension = ''
    if(post.is_video):
        extension = EXTENSION_VIDEO
    else:
        extension = EXTENSION_IMAGE

    for file in os.listdir(target):
        if file.endswith(extension):
            return file


app.run(
    host=AUTBOT_HOST,
    port=AUTBOT_PORT,
    debug=True,
)
