from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_file
import instaloader
import configparser
import os

parser = configparser.ConfigParser()
parser.read('autobot.config')

AUTBOT_HOST = parser.get('autobot', 'host')
AUTBOT_PORT = parser.get('autobot', 'port')

POST_PREFIX = parser.get('post', 'prefix')

EXTENSION_IMAGE = parser.get('extension', 'image')
EXTENSION_VIDEO = parser.get('extension', 'video')
MIMETYPE_IMAGE = parser.get('mimetype', 'image')
MIMETYPE_VIDEO = parser.get('mimetype', 'video')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


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
        filename, mimetype = download_post(username, password, id, target)

        if not download == None:
            return send_file(os.path.join(target, filename), mimetype=mimetype)

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
    mimetype = ''
    if(post.is_video):
        extension = EXTENSION_VIDEO
        mimetype = MIMETYPE_VIDEO
    else:
        extension = EXTENSION_IMAGE
        mimetype = MIMETYPE_IMAGE

    for file in os.listdir(target):
        if file.endswith(extension):
            return file, mimetype


app.run(
    host=AUTBOT_HOST,
    port=AUTBOT_PORT,
    debug=True,
)
