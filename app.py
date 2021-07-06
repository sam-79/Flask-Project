
# server.py file for heroku web hosting
from flask import Flask, render_template, request, jsonify
from flask.helpers import send_file
import pafy, requests, io, os
from instaloader import Instaloader, Post, Profile
from currencies import allcurrencies
from database import DataBase
from decouple import config
from PDFutility import *

Sname = 'Online Tools' #Header name of site
app = Flask(__name__)
app.debug = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS']= ['jpg', 'png', 'webp', 'jpeg', "pdf"]

"""
#Create instance of Instaloader
L = Instaloader()
try:
    L.login(config('insta_username',default=os.getenv('insta_username')),config('insta_password',default=os.getenv('insta_password')))
except:
    L.load_session_from_file(config('insta_username',default=os.getenv('insta_username')))
"""

# Home Page
@app.route('/')
def home():
    return render_template('home.html',Sname=Sname)

# Login Page
@app.route('/about.html')
def about():
    return render_template('AboutMe.html',Sname=Sname)

# Contact Page
@app.route('/contact.html')
def contact():
    return render_template('contact.html',Sname=Sname)

@app.route('/contact/thanks', methods=['POST'])
def contactRes():
    try:
        values = request.data.decode().split(sep=",")
        print(values,values[0], values[1], values[2], values[3])
        data = [values[0], values[1], values[2], values[3]]
        obj = DataBase()
        obj.Add(data)
        obj.close()
        return jsonify({'msg':f"Thank You {values[0]} for your valuable feedback"})
        # return "done"
    except Exception as exp :
        return jsonify({'msg':f"Error {exp}"})


# Login Page
@app.route('/login.html')
def login():
    return render_template('login.html',Sname=Sname)


# Youtube Downloader Page
@app.route('/YTDownloader.html')
def YdownloaderForm():
    return render_template("YTDownloader.html",Sname=Sname)

# Youtube Result Request
@app.route('/ytresult', methods=['POST'])
def Ydownloader():

    try:
		
        video = pafy.new(request.data.decode().split(sep=',')[0])
        title = video.title
        duration = video.duration
        thumb = video.thumb

        x = request.data.decode().split(sep=',')[1]
        if (x == 'audiostreams'):
            stream = video.audiostreams
        elif(x == 'streams'):
            stream = video.streams
        elif(x == 'allstreams'):
            stream = video.allstreams

        streaminfo = {}

        for i, j in zip(stream, range(len(stream))):
            streaminfo["yt"+str(j)] = [i.extension, i.quality,
                                       round(i.get_filesize()/(1024*1024), 2), i.url_https]
            #print("data",type(i.quality),type(i.extension), type(i.url_https) ,type(i.get_filesize()))

        print(streaminfo)

        data = {
            'length': len(stream),
            'title': title,
            'duration': duration,
            'thumbnail': thumb,
            'streams': streaminfo,
        }

        print('data\n', data, type(data))
        return jsonify(data)

    except Exception as exp:
        return jsonify({'Error': f'{exp}'})
    


# Instagram Downloader
@app.route('/instaDownloader.html')
def instadownloaderForm():
    return render_template("instaDownload.html",Sname=Sname)

# Instagram Post Request
@app.route('/insta-post-result', methods=['POST'])
def instaPostDownloader():
    
    shortcode = (request.data.decode().split(sep='/'))[4]
    
    try:
        #Post instances
        post = Post.from_shortcode(L.context, shortcode)
        #result list
        posts = []
        
        if(post.mediacount>1):
            for i,j in zip(range(post.mediacount), post.get_sidecar_nodes()):
                if(j.is_video):
                    posts.append(j.video_url)
                else:
                    posts.append(j.display_url)
        else:
            if(post.is_video):
                posts.append(post.video_url)
            else:
                posts.append(post.url)
        
        return jsonify({'Username' : post.owner_username , 'posts' : posts})

    except Exception as exp:
        return jsonify({'Error': f'{exp}'})

#Instagram Profile Pic
@app.route('/instaProfileDownloader.html')
def instaProfileDownloaderForm():
    return render_template("instaProfileDownload.html",Sname=Sname)

#Instagram Profile Pic Request
@app.route('/insta-profile-result', methods=['POST'])
def instaProfileDownloader():
    
    username = (request.data.decode().split(sep='/'))[3]
    
    try:
        #Post instances
        profile = Profile.from_username(L.context, username)
        #result list
        posts = []
        
        return jsonify({'Username' : username , 'link' : profile.profile_pic_url})

    except Exception as exp:
        return jsonify({'Error': f'{exp}'})


# Currency Converter 
@app.route('/currency-converter.html')
def cc():
    return render_template('currencycnvt.html', currency=allcurrencies(),Sname=Sname)

@app.route('/ccresult', methods=['GET'])
def ccresult():
    try:
        key = config('currencylayer_key', default=os.getenv('currencylayer_key'))
        data = requests.get(f'http://api.currencylayer.com/live?access_key={key}').json()
        return jsonify(data['quotes'])
    except Exception as exp:
        return jsonify({'Error': f'{exp}'})


#image2pdf
@app.route('/image-to-pdf.html')
def img2pdf():
    return render_template('img2pdf.html',Sname=Sname)

@app.route('/imgtoPDFoutput.pdf',methods=['POST'])
def imgtoPDFoutput():
    
    imgBytesIO=[]

    for i in request.files.getlist('files'):
        if i.filename != '' :
            file_ext = (i.filename).split(sep='.')[-1]
            
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return bad_request(0)
            
            in_memory_file = io.BytesIO()
            i.save(in_memory_file)
            imgBytesIO.append(in_memory_file)
    
    #here in x we get bytes data of generated PDF file
    x=imagetoPDF(imgBytesIO)
    
    if(x!="Error"):
        #here in send_file first parameter in filename or fp, so we are passing fp
        #as_attachment = True -> File directly downloads
        return send_file(io.BytesIO(x), mimetype='application/pdf', attachment_filename='output.pdf',as_attachment=False)
    else:
        #return f" <h1> {x['error']} </h1>"
        return bad_request(x['error'])

#Encrypt PDF
@app.route('/encrypt-pdf.html')
def encryptpdf():
    return render_template('encryptPDF.html', Sname=Sname)

@app.route('/encryptedPDFoutput.pdf',methods=['POST'])
def encryptedPDFoutput():

    pdfile = request.files['files']
    password = request.form['password']

    if pdfile.filename != '' :
        file_ext = (pdfile.filename).split(sep='.')[-1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return bad_request(0)
            
        in_memory_file = io.BytesIO()
        pdfile.save(in_memory_file)
    
    #here in x we get bytes data of generated PDF file
    x = encryptPDF(in_memory_file, password)
    
    if(type(x)!=dict):
        #here in send_file first parameter in filename or fp, so we are passing fp
        #as_attachment = True -> File directly downloads
        return send_file(io.BytesIO(x), mimetype='application/pdf', attachment_filename='output.pdf',as_attachment=False)
    else:
        #return f" <h1> {x['error']} </h1>"
        return bad_request(x['error'])

#Decrypt PDF
@app.route('/decrypt-pdf.html')
def decryptpdf():
    return render_template('decryptPDF.html', Sname=Sname)

@app.route('/decryptedPDFoutput.pdf',methods=['POST'])
def decryptedPDFoutput():

    pdfile = request.files['files']
    password = request.form['password']

    if pdfile.filename != '' :
        file_ext = (pdfile.filename).split(sep='.')[-1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return bad_request(0)
            
        in_memory_file = io.BytesIO()
        pdfile.save(in_memory_file)
    
    #here in x we get bytes data of generated PDF file
    x = decryptPDF(in_memory_file, password)
    
    if(type(x)!=dict):
        #here in send_file first parameter in filename or fp, so we are passing fp
        #as_attachment = True -> File directly downloads
        return send_file(io.BytesIO(x), mimetype='application/pdf', attachment_filename='output.pdf',as_attachment=False)
    else:
        #return f" <h1> {x['error']} </h1>"
        return bad_request(x['error'])


#Merge PDF
@app.route('/merge-pdf.html')
def mergepdf():
    return render_template('mergePDF.html', Sname=Sname)

@app.route('/mergedPDFoutput.pdf',methods=['POST'])
def mergedPDFoutput():

    pdfBytesIO=[]

    for i in request.files.getlist('files'):
        if i.filename != '' :
            file_ext = (i.filename).split(sep='.')[-1]
            
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return bad_request(0)
            
            in_memory_file = io.BytesIO()
            i.save(in_memory_file)
            pdfBytesIO.append(in_memory_file)
    
    #here in x we get bytes data of generated PDF file
    x=mergePDF(pdfBytesIO)
    
    if(type(x)!=dict):
        #here in send_file first parameter in filename or fp, so we are passing fp
        #as_attachment = True -> File directly downloads
        return send_file(io.BytesIO(x), mimetype='application/pdf', attachment_filename='output.pdf',as_attachment=False)
    else:
        #return f" <h1> {x['error']} </h1>"
        return bad_request(x['error'])



# Error handlings
@app.errorhandler(400)
def bad_request(e):
    return render_template('Errors/bad_request.html',Sname=Sname)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('Errors/page_not_found.html',Sname=Sname)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('Errors/internal_server_error.html',Sname=Sname)



#For PWA
#ServiceWorker
@app.route("/service-worker.js")
def sw():
    return app.send_static_file("js/sw.js")


#Manifest
@app.route("/static/manifest.json")
def manifest():
    return send_file("static/manifest.webmanifest")


#offine
@app.route("/offline")
def offline():
    return send_file("templates/offline.html")


#favicon
@app.route("/favicon.ico")
def favicon():
    return send_file("static/images/icons/favicon.ico", mimetype="image/x-icon")




if(__name__ == '__main__'):
    app.run()
