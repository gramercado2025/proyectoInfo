from django.shortcuts import render, redirect
from .forms import RegistroForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages



# Create your views here.
def registro(request):
    if request.method=='POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_auth:login')
    else:
        form = RegistroForm()       # En este caso no es un POST, entonces es un get

    return render(request, "registro.html", {'form':form}) # Como contexto le paso form



def login_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # ... (código de autenticación)
            user = form.get_user() # Método más limpio para obtener el usuario autenticado

            if user is not None: 
                auth_login(request, user) # 🚨 Usar el alias
                messages.success(request, f"Bienvenido {user.username}")
                # Si hay un parámetro 'next', redirige allí; si no, al 'index'
                next_url = request.POST.get('next') or request.GET.get('next') or 'index'
                return redirect(next_url) 
            
        # Si el formulario NO ES VÁLIDO o user es None, el código continúa
        # hasta el return render final para mostrar los errores.
    
    else:
        form = AuthenticationForm(request) # Es buena práctica pasar 'request'
        
    # Renderiza la plantilla (muestra errores si el POST falló)
    return render(request, 'login.html', {"form": form})

def logout_usuario(request): 
    auth_logout(request)      
    return redirect('blog_auth:login') 
                        
