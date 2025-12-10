from django.shortcuts import render, redirect
from .forms import RegistroForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.
def registro(request):
    if request.method=='POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()       # En este caso no es un POST, entonces es un get

    return render(request, "auth/registro.html", {'form':form}) # Como contexto le paso form

def login(request):
    if request.method=='POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username=form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

        if user:        #Si se pudo autenticar
            login(request, user)
            messages.success(request, f"Bienvenido {username}") # Mensajeria interna 
        return redirect('index')                                # El index este es el index_final?
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {"form":form})

def logout(request):
    logout(request)
    return redirect('login')
                        
