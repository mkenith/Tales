from django.shortcuts import render
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import json
from .models import * 
from django.apps import apps
#initialize  app  config
from django.apps import AppConfig
#creating segmentation
import pixellib
import cv2
from pixellib.instance import custom_segmentation
import os
# creating an stl file 
import numpy as np
from stl import mesh
from PIL import Image, ImageOps, ImageFont, ImageDraw


print("*********At Views**********")
default_path=os.getcwd()
def tales(request): 
    segment_image_animals.inferConfig(num_classes=4, class_names=["BG", "butterfly","squirrel","dog","elephant"])
    segment_image_animals.load_model("mask_rcnn_model.013-0.350316.h5")                                                                                                                                                  
    print("Rendering Homepage")
    return render(request,'Web_App/home.html')
def upload(request):
    print("Upload using Ajax")
    response_data={
        'data':"no_image",
        'valid':"no"
    }
    if request.method == 'POST':
        pPicture=request.FILES.get('img',None)
        if pPicture is not None and pPicture != '':
            fs = FileSystemStorage()
            filename = fs.save(pPicture.name, pPicture)
            object_name = ImageSegmentation_animals(filename)
            convertToSTL("segmented_object_1.jpg",object_name,media_url)
            response_data = {
                'data': "segmented_image_"+filename+"/output.stl",
                'valid':"yes"
            }
    return HttpResponse(json.dumps(response_data))

def ImageSegmentation_animals(imagename):
    print("Segmenting Image")
    #change the classes dictionary into tagalog, or cebuano
    classes = {1:"butterfly",
           2:"squirrel",
           3:"dog",
           4:"elephant"}
    #create a directory
    os.chdir(default_path)
    current_dir = os.getcwd()
    prev_dir = current_dir
    dir = os.path.join(current_dir,"segmented_image_"+imagename)
    if not os.path.exists(dir):
        os.mkdir(dir)
        os.chdir(dir)
        prev_dir = os.path.join(prev_dir,imagename)
        print("PREV DIR = "+prev_dir)
    segmask,output = segment_image_animals.segmentImage(prev_dir,extract_segmented_objects=True, save_extracted_objects=True)
    if os.path.exists(prev_dir):
        os.remove(prev_dir)
    key=segmask.get('class_ids')
    print(classes[key[0]])
    return classes[key[0]]
    
def convertToSTL(filename,object_name,media_url):
    stl = ImageToSTL(filename,object_name,media_url)
    stl.configure()
    stl.convertToSTL()

class ImageToSTL:
    def __init__(self,filename_in,object_name,media_url):
        print("####### HERE AT INIT STL ######")
        font_url = os.path.join(media_url,"testbraille.ttf")
        self.max_size      = (500,500)         # Size of canvas
        self.max_height    = 10                # Setting the max_height of the z coordinates
        self.min_height    = 0                 # Setting the min_height of the z coordinates
        self.bkgnd_thres   = 0.25              # For removing unnecessary faces
        self.filename_in   = filename_in       # Name of input file [.png, .jpg, .jpeg]
        self.filename_out  = 'output'          # Name of output file [.stl (no need to add extension)] || adding location is '/' not '\'
        self.is_inverted   = False             # If colors are inverted (Color Black should be the background)
        self.object_name   = object_name       # Text in the bottom
        self.font_family   = font_url          #"BrailleNormal-lLDX.ttf" 
        self.width_ratio   = .75               # Width ratio of the text at the bottom
    def configure(self):
        print(os.listdir(os.getcwd()))
        im = Image.open(self.filename_in)
        if(self.is_inverted):
            im = ImageOps.invert(im.convert('RGB'))

        im.thumbnail(self.max_size)
        (ncols,nrows)=im.size

        font_size = self.find_font_size(self.object_name, self.font_family ,im, self.width_ratio)
        font = ImageFont.truetype(self.font_family, font_size)
        w, h = ImageDraw.Draw(im).textsize(self.object_name,font=font)

        img1 = Image.new( mode = "RGB", size = (ncols + 8, nrows + 8 + h +  4))
        img1.paste(im, [4,4])
        img = Image.new('RGB', (w+4, h+4), color = (10,10,10))
        img1.paste(img, [round((ncols - w)/2) - 4,nrows + 4])

        draw = ImageDraw.Draw(img1)

        draw.text(((ncols - w)/2, nrows + 8), self.object_name ,(65,65,65),font=font)
        self.grey_img = img1.convert('L') # Convert into greyscale (L) [w/o Alpha] Luminance

    def find_font_size(self,text, font, image, target_width_ratio):
        tested_font_size = 100
        tested_font = ImageFont.truetype(font, tested_font_size)
        observed_width, observed_height = self.get_text_size(text, image, tested_font)
        estimated_font_size = tested_font_size / (observed_width / image.width) * target_width_ratio
        return round(estimated_font_size)
    
    def get_text_size(self,text, image, font):
        im = Image.new('RGB', (image.width, image.height))
        draw = ImageDraw.Draw(im)
        return draw.textsize(text, font)

    def convertToSTL(self):
        imageNp = np.array(self.grey_img)
        maxPix=imageNp.max()
        minPix=imageNp.min()

        (ncols,nrows)=self.grey_img.size
        vertices=np.zeros((nrows,ncols,3))

        for x in range(0, ncols):
            for y in range(1, nrows):
                pixelIntensity = imageNp[nrows - y][x]
                z = (pixelIntensity / maxPix)  * self.max_height
                vertices[y][x]=(x, y, z)

        # Smoothing the value by averaging the individual vertices
        vertices_temp = np.copy(vertices)

        for x in range(1, ncols-1):
            for y in range(1, nrows-1):
                pixelIntensity= np.sum( vertices_temp[y-1:y+2 ,x-1:x+2,2], dtype=np.float32)
                z = pixelIntensity / 9
                vertices[y][x]=(x, y, z)

        # Creating the faces using the smoothen out vertices
        faces=[]
        for x in range(1, ncols-2):
            for y in range(1, nrows-2):
                # create face 1
                v1 = vertices[y][x]
                v2 = vertices[y+1][x]
                v3 = vertices[y+1][x+1]
                
                if(v1[2] >= self.bkgnd_thres or v2[2] >= self.bkgnd_thres or v3[2] >= self.bkgnd_thres):
                    face = np.array([v1,v2,v3])
                    faces.append(face)
                    #for bottom part
                    face = np.array([[v1[0],v1[1], v1[2] <= self.bkgnd_thres and v1[2] or self.min_height],[v2[0],v2[1], v2[2] <= self.bkgnd_thres and v2[2] or self.min_height],[v3[0],v3[1],v3[2] <= self.bkgnd_thres and v3[2] or self.min_height]])
                    faces.append(face)

            # create face 2 it also uses v1 & v2 with the same value
            v2 = vertices[y][x+1]

            if(v1[2] >= self.bkgnd_thres or v2[2] >= self.bkgnd_thres or v3[2] >= self.bkgnd_thres):
                face = np.array([v1,v2,v3])
                faces.append(face)
                #for bottom part
                face = np.array([[v1[0],v1[1], v1[2] <= self.bkgnd_thres and v1[2] or self.min_height],[v2[0],v2[1], v2[2] <= self.bkgnd_thres and v2[2] or self.min_height],[v3[0],v3[1],v3[2] <= self.bkgnd_thres and v3[2] or self.min_height]])
                faces.append(face)

        print(f"number of faces [triangles]: {len(faces)}")
        facesNp = np.array(faces)
        # Create the mesh
        surface = mesh.Mesh(np.zeros(facesNp.shape[0] + 1, dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                surface.vectors[i][j] = facesNp[i][j]

        # Write the mesh to file = filename_out + .stl
        surface.save( self.filename_out + '.stl')