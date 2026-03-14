from django.shortcuts import render


def home(request):
    return render(request, 'calculator/home.html')

# Create your views here.
