import linearProcess
import os
import sys
import pandas as pd
import numpy as np
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, make_response, Response, send_file
from werkzeug.utils import secure_filename
from format_table import write_to_html_file
# import time
# import redis


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

# redis_host = "localhost"
# redis_port = 6379
# redis_password = ""
# r = redis.StrictRedis(
#   host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pre_buildDays = request.values['prebuildDay']
        if 'file' not in request.files:
            return render_template('index.html',title='error',content='No file attached in request')     
        file = request.files['file']
        if allowed_file(file.filename) == False:
            return render_template('index.html',title='error',content='Please upload a CSV file')     
        try:
            pre_buildDays = int(pre_buildDays)
        except ValueError:
            return render_template('index.html',title='error',content='You must enter an valid integer')     
        if pre_buildDays == 0:
            return render_template('index.html',title='error',content='Mission Impossible! (Not allowed to prebuild)')     
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("CSV file saved")
            return process_file(filename, pre_buildDays)
    return render_template('index.html',title='input')


def process_file(filename, pre_buildDays):
    # print('!yay!')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_name, preview = linearize(filepath, filename, pre_buildDays)
    return render_template('index.html', title=output_name, content=preview)


# @app.route('/progress')
# def getProgress():
#   """Get percentage progress for auto attribute process"""
#   r.set("progress", str(0))
#   def progress_stream():
#     p = int(r.get("progress"))
#     while p < 100:
#       p = int(r.get("progress"))
#       p_msg = "data:" + str(p) + "\n\n"
#       yield p_msg
#       # Client closes EventSource on 100%, gets reopened when `submit` is pressed
#       if p == 100:
#         r.set("progress", str(0))
#       time.sleep(1)
#   return Response(progress_stream(), mimetype='text/event-stream')

# process the uploaded file
def linearize(filepath, filename, pre_buildDays):
    result = linearProcess.linearize(filepath, pre_buildDays)
    output_name = f'output-{pre_buildDays}.csv'
    result.to_csv(os.path.join(app.config['DOWNLOAD_FOLDER'], output_name), index=False)
    formated_preview = write_to_html_file(result, 'Preview of Suggested Production Plan')
    # send_from_directory(app.config['DOWNLOAD_FOLDER'], output_name, as_attachment=True)
    return output_name, formated_preview

# use title to pass in output filename
@app.route('/return-files/<title>')
def return_files_tut(title):
	try:
		return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], title), as_attachment=True)
	except Exception as e:
		return str(e)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)