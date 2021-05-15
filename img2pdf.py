from PIL import Image
import io

def imagetopdf(rawdata:list):
    # rawdata -> list of BytesIO of images
    # file -> name of first image file
    # return -> bytes data of created pdf
    im=[]
    
    mywidth = 794
    #hei = 1123
    try:
        for i in rawdata:
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