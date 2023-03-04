from flask import Flask, request, jsonify
from main import setup_embeds, load_model, search_videos

from test import generate_all_thumbnails
from pathlib import Path
# from .test import generate_all_thumbnails


app = Flask(__name__)
model, tokenizer, preprocess = load_model()

@app.route('/setup', methods=['GET'])
def get_path():
    path=str(request.args['path'])
    setup_embeds(path, model, preprocess)
    thumbnails = generate_all_thumbnails(path)
    print(thumbnails)
    return jsonify({"status": True, "thumbnails":thumbnails})

@app.route('/search', methods=['GET'])
def search():
    search=str(request.args['query'])
    path=str(request.args['path'])
    output_ls = search_videos(search, path, model, tokenizer)
    print(output_ls)
    
    return jsonify({"vid_paths": list(map(str,map(Path,[o[0] for o in output_ls])))})
    # return jsonify({"vid_paths": list(map(str(Path),[o[0] for o in output_ls]))})

if __name__=="__main__":
    app.run()