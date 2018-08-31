from PIL import Image
import os


class Compression():
        
    def doCompress(self,fileName,width,height):
        path = os.getcwd()
        image = Image.open(path+str("\\")+ fileName)
        newImage = image.resize((width,height))
        newImage.save("small_"+str(fileName), 'BMP', dpi=[width,height], quality=90)
        return True
        


        
        