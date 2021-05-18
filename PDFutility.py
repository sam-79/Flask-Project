from PIL import Image
import io
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

def imagetoPDF(iodata:list):
    # iodata -> list of BytesIO of images
    # return -> bytes data of created pdf
    im=[]
    
    mywidth = 794
    #hei = 1123
    try:
        for i in iodata:
            img = Image.open(i)

            if(img.size[0]>img.size[1]):
                mywidth = 1123

            wpercent = (mywidth/float(img.size[0]))
            hsize = int(float(img.size[1])*float(wpercent))

            img = img.convert('RGB')
            img=img.resize((mywidth,hsize),Image.ANTIALIAS)
            # img=img.resize((int(img.size[0]/2),int(img.size[1]/2)),Image.ANTIALIAS)
            im.append(img)
        in_memory=io.BytesIO() #memory buffer

        im[0].save(in_memory,format='pdf',save_all=True,append_images=im[1:])

        return in_memory.getvalue()
    except Exception as exp:
        print(exp)
        return "Error"

def encryptPDF(pdfile: io.BytesIO, password: str):
    #pdfile -> io.BytesIO
    #return -> io.BytesIO

    try:
        #instance of PdfFileWriter class
        output = PdfFileWriter()
        input = PdfFileReader(io.BufferedReader(pdfile), strict=False)
        
        in_memory=io.BytesIO() #memory buffer
        output.cloneReaderDocumentRoot(input)
        output.encrypt(password)
        output.write((in_memory))

        return in_memory.getvalue()

    except Exception as exp:
        return {"error":exp.args[0]}

def decryptPDF(pdfile: io.BytesIO, password: str):
    #pdfile -> io.BytesIO
    #return -> io.BytesIO

    try:
        #instance of PdfFileWriter class
        output = PdfFileWriter()
        input = PdfFileReader(io.BufferedReader(pdfile), strict=False)
        
        if(input.isEncrypted):
            input.decrypt(password)
        else:
            return pdfile.getvalue()
        
        in_memory=io.BytesIO() #memory buffer
        output.cloneReaderDocumentRoot(input)
        output.write((in_memory))

        return in_memory.getvalue()

    except Exception as exp:
        return {"error":exp.args[0]}


def mergePDF(iodata:list):
    # rawdata -> list of BytesIO of images
    # return -> bytes data of created pdf
    try:
        output = PdfFileMerger()
        for pdf in iodata:
            input = io.BufferedReader(pdf)
            output.append(fileobj = input)
        
        in_memory = io.BytesIO()

        output.write(in_memory)
        return in_memory.getvalue()

    except Exception as exp:
        return {"error":exp.args[0]}
    