from django.shortcuts import render

def home(request):
    print('hello')
    return render(request, 'index.html')
