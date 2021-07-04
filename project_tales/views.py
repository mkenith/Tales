from django.shortcuts import render
from django.views.generic import View

# Create your views here.

class TalesView(View):
    def get(self,request):
        print('get')
        return render(request,'Web_App/home.html')