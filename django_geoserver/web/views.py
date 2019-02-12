from django.shortcuts import render

# Create your views here.
def index(request):
    testVar = "hello"
    return render(request, 'web/index.html', {'testVar' : testVar})