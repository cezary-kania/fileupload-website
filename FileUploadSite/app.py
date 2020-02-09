import os,json,random,string
from flask import Flask, request, redirect, url_for, abort,render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB

def GetFileProps(upload_id):
    fileList = LoadUploadsList('uploads_details.json')['files']
    for file in fileList:
        if file['upload_id'] == upload_id:
            return file
    return None

def GenerateUploadId(uploads_list):
    while True:
        newId = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        if newId not in [upload['upload_id'] for upload in uploads_list]:
            return newId

def LoadUploadsList(listFile):
    with open(listFile) as json_file:
        return json.load(json_file)

def UpdateUploadsList(listFile,data):
     with open(listFile, 'w') as json_file:
        json.dump(data,json_file,indent=3)

@app.route('/uploads/<upload_id>')
def uploaded_file(upload_id):
    file = GetFileProps(upload_id)
    if file == None:
        abort(404)
    fileExt = file['fileExt']
    filePath = os.path.join(app.config['UPLOAD_FOLDER'], f'{upload_id}.{fileExt}')
    return render_template('filepage.html',filename=file["filename"],filePath=filePath)

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file is not None:
            filename = secure_filename(file.filename)
            uploadsList = LoadUploadsList('uploads_details.json')
            newUpload_id = GenerateUploadId(uploadsList['files'])
            fileExt = filename.split(".")[1]
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], f'{newUpload_id}.{fileExt}')
            file.save(filePath)
            uploadsList['files'].append({
                "upload_id": newUpload_id,
                "filename": filename,
                "fileExt" : fileExt,
                "file_size": os.stat(filePath).st_size
            })
            UpdateUploadsList('uploads_details.json',uploadsList)    
            return redirect(url_for('uploaded_file',upload_id=newUpload_id))
    return render_template('index.html')

app.run(debug=True)

