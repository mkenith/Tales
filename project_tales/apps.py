from django.apps import AppConfig
import pixellib
import cv2
from pixellib.instance import custom_segmentation
import os


class ProjectTalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_tales'
    def __init__(self,app_name,app_module):
        AppConfig.__init__(self,app_name, app_module)
        print("AppCofig Initilizing...")
        current_dir = os.getcwd()
        dir = os.path.join(current_dir,"media")
        if os.path.exists(dir):
            os.chdir(dir)
            print(dir)