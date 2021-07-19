from django.shortcuts import render
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

#import pixellib
#from pixellib.custom_train import instance_custom_training
#from pixellib.instance import custom_segmentation
# Create your views here.

class TalesView(View):
    def get(self,request):
        print("here sa get")
        return render(request,'Web_App/home.html')
    def post(self,request):
        if request.method == 'POST':
            if 'upload' in request.POST:
                pPicture=request.FILES.get('imagefile',None)
                if pPicture is not None and pPicture != '':
                    fs = FileSystemStorage()
                    filename = fs.save(pPicture.name, pPicture)
                    pPicture = fs.url(filename)
                    print(pPicture)
                    #prepare(pPicture)
        #return render(request,'Web_App/home.html')
        return HttpResponse("uploaded")
#not working
#
#def prepare(imageurl):
#   if imageurl!='':
#       print(imageurl)
#       segment_image = custom_segmentation()
#       segment_image.inferConfig(num_classes= 4, class_names= ["BG", "butterfly","squirrel","dog","elephant"])
#       segment_image.load_model("mask_rcnn_model.013-0.350316.h5")    
#       print("here")
#       segment_image.segmentImage(imageurl,output_image_name="masked_image.jpg",extract_segmented_objects=True, save_extracted_objects=True)
#       print("here2")
#   else:
#       print("image url is empty")
        
