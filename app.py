
# server.py file for heroku web hosting
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pafy, requests
from instaloader import Instaloader, Post
from currencies import allcurrencies
from database import DataBase
from decouple import config


Sname = 'Online Tools' #Header name of site
UPLOAD_FOLDER = '/temp'
app = Flask(__name__)
app.debug = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# Instagram Result Request
@app.route('/instaresult', methods=['POST'])
def instadownloader(login=True, username = config('insta_username',default=''),password=config('insta_password',default='')):
    
    shortcode = (request.data.decode().split(sep='/'))[4]
    #Create instance of Instaloader
    L = Instaloader()
    L.login(username,password)


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


# Currency Converter 
@app.route('/currency-converter.html')
def cc():
    return render_template('currencycnvt.html', currency=allcurrencies(),Sname=Sname)

@app.route('/ccresult', methods=['GET'])
def ccresult():
    try:
        key = config('currencylayer_key', default='')
        data = requests.get(f'http://api.currencylayer.com/live?access_key={key}').json()
        return jsonify(data['quotes'])
    except Exception as exp:
        return jsonify({'Error': f'{exp}'})

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


if(__name__ == '__main__'):
    app.run()
