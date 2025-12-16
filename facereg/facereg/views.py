from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .utils import classify_face
import base64
from login.models import Log
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from profiles.models import Profile
from .forms import SignUpForm

def homepage(request):
  return render(request, 'index.html')

@login_required
def editor(request):
  return render(request, 'editor.html')

def signup_view(request):
  form = SignUpForm()
  return render(request, 'signup.html', {"form": form})

def login_view(request):
  return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def register(request):
  if request.method == "POST":
    form = SignUpForm(request.POST)
    
    if form.is_valid():
      user = form.save(commit=False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('/')
    else:
      return render(request, 'signup.html/', {'form': form})

def signin(request):
  is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
  
  if is_ajax:
    photo = request.POST.get('photo')
    _, str_img = photo.split(';base64')
    decoded_file = base64.b64decode(str_img)
    x = Log()
    x.photo.save('upload.png', ContentFile(decoded_file))
    x.save()
    qs = Profile.objects.all()
    
    for p in qs:
        photoPath = str(p.photo.path)
        print(photoPath)
        
    res = classify_face(x.photo.path)
    print(res) # print name of the user after classify the face
    
    if res:
      user_exists = User.objects.filter(username = res).exists()
      if user_exists:
        user = User.objects.get(username = res)
        profile = Profile.objects.get(user = user)
        x.profile = profile
        x.save()
        login(request, user)
        return JsonResponse({'status': 'login successful!'})
    return JsonResponse({'status': 'login failed!'})
