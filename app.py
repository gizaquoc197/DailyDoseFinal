import asyncio
import logging
from flask import Flask, render_template, request, jsonify
from shazamio import Shazam
import requests

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_type = extract_search_type(search_query)
        result = get_search_result(search_query, search_type)
        print(result)   
    return render_template('index.html', result=result, search_query=request.form.get('search_query'))

@app.route('/shazam', methods=['GET'])
def shazam():
    return render_template('shazam.html')
@app.route('/elements', methods=['GET', 'POST'])
def elements():
    return render_template('elements.html')

@app.route('/recognize_music', methods=['POST'])
async def recognize_music_from_frontend():
    logging.info("Received a POST request")

    audio_data = request.files.get('audio_data')

    if audio_data:
        audio_path = 'temp_audio.ogg'
        audio_data.save(audio_path)

        try:
            result = await recognize_music(audio_path)
            logging.info(f"Recognition result: {result}")
            return jsonify({'result': result})
        except Exception as e:
            logging.error(f"Recognition error: {e}")
            return jsonify({'error': str(e)})

    logging.warning("No audio data received")
    return jsonify({'error': 'No audio data received'})

async def recognize_music(file_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        shazam = Shazam()
        out = await shazam.recognize_song(file_path)
        print(out)
        return out
    finally:
        loop.close()

def extract_search_type(search_query):
    prefix = "Random"
    if search_query.startswith(prefix):
        return search_query[len(prefix):].strip().lower()
    else:
        return "default"

def get_search_result(search_query, search_type):
    API_KEY = open('API_KEY').read()
    SEARCH_ENGINE_ID = open('SEARCH_ENGINE_ID').read()

    target_sites = {
        'memes': 'https://www.memedroid.com/memes/',
        'quotes': 'https://www.brainyquote.com/',
        'jokes': 'https://icanhazdadjoke.com/',
        'videos': 'https://www.youtube.com/',
        'music': 'https://www.spotify.com/',
        'default': ''
    }

    if search_type not in target_sites:
        return "Invalid search type"

    target_site = target_sites[search_type]
    url = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': search_query,
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'gl': "us",
        'lr': "lang_en",
        'num': 1,
        'siteSearch': target_site
    }

    response = requests.get(url, params=params)
    results = response.json()

    if 'items' in results:
        return results['items'][0]['link']
    else:
        return "No result found"
    
if __name__ == '__main__':
    app.run(debug=True)
