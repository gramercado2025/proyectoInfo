from django.shortcuts import render, get_object_or_404,redirect #luego de hacer comentario para que no de error
from django.http import HttpResponse
from .models import Post, Autor, Comentario, Categoria
from django.db.models import Count
from .forms import FormularioComentario, PostForm
from django.core.paginator import Paginator # Para la paginacion
from django.db.models import Count
from django.template.loader import render_to_string #para mostrar comentarios filtrados sin recargar la pagina
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail


def home(request):
    
    # --- 1. Obtener parámetros de ordenación y búsqueda ---
    orden = request.GET.get('order_by', 'reciente') 
    search_term = request.GET.get('q')

    # --- 2. Post Destacado ---
    # Lo obtenemos y anotamos aparte, ya que lo excluiremos de la lista principal.
    post_destacado = Post.objects.filter(es_destacado=True).annotate(total_comentarios=Count('comentarios')).first()   
    
    # --- 3. Definición BASE de la lista de Posts (IMPORTANTE: Se define SIEMPRE) ---
    # Usaremos 'posts' como nuestra variable principal para la consulta.
    # posts = Post.objects.all().annotate(total_comentarios=Count('comentarios')).order_by(-"fecha_creacion")
    posts = Post.objects.all().annotate(total_comentarios=Count('comentarios'))
    # 4. Excluir el post destacado
    if post_destacado:
        posts = posts.exclude(id_post=post_destacado.id_post)

    # --- 4. Aplicar ORDENACIÓN ---
    if orden == 'antiguedad':
        posts = posts.order_by('fecha_creacion') 
    elif orden == 'alfabetico_asc':
        posts = posts.order_by('titulo') 
    elif orden == 'alfabetico_desc':
        posts = posts.order_by('-titulo')
    else: # 'reciente' (o cualquier otro valor por defecto)
        posts = posts.order_by('-fecha_creacion')
        
    # --- 5. Aplicar FILTRO DE BÚSQUEDA ---
    if search_term:
        posts = posts.filter(titulo__icontains=search_term)
        
    # --- 6. Excluir Post Destacado de la lista principal (Lógica de Limpieza) ---
    if post_destacado:
        # Aquí usamos 'posts', que es la variable principal que estamos construyendo.
        # posts = posts.exclude(id=post_destacado.id) # Usa 'id' si ese es el nombre de tu PK
        posts = posts.exclude(id_post=post_destacado.id_post)
    # -----------------------------------------------------------------
    # Línea de Paginación (Ahora siempre accederá a 'posts')
    # -----------------------------------------------------------------
    
    # Nota: Tu código tenía dos paginaciones, simplificamos a una sola.
    posts_por_pagina = 4 
    paginator = Paginator(posts, posts_por_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        # Enviamos la lista paginada ('page_obj') en lugar de la consulta completa.
        "posts": page_obj.object_list, 
        "post_destacado": post_destacado,
        "orden_actual": orden,
        "page_obj": page_obj, # El objeto de paginación completo
    }

    return render(request, 'index_final.html', context)

def detalle_articulo(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comentarios_qs = post.comentarios.all() 
    orden = request.GET.get('orden', 'mas_nuevo')    
    if orden == 'mas_nuevo':
        comentarios_qs = comentarios_qs.order_by('-fecha_comentario') 
    elif orden == 'mas_antiguo':
        comentarios_qs = comentarios_qs.order_by('fecha_comentario') 

    #filtrando por usuario
    autor_id_filtro = request.GET.get('autor_id')
    autor_filtrado = None
    if autor_id_filtro:
        try:
            autor_filtrado = User.objects.get(id=autor_id_filtro)
            comentarios_qs = comentarios_qs.filter(autor_comentario=autor_filtrado)
        except User.DoesNotExist:
            pass
    if request.method == 'POST':
        form = FormularioComentario(request.POST)
        
        if not request.user.is_authenticated:# Redirigir al login si no logeo
            return redirect('blog_auth:login') 

        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.post = post 
            nuevo_comentario.autor_comentario = request.user 
            nuevo_comentario.save()
            return redirect('detalle_articulo', pk=post.pk)            
    else:
        form = FormularioComentario()
        
    context = {
        "post": post,
        "comentarios": comentarios_qs, 
        "form_comentario": form,
        "orden_actual": orden,           
        "autor_filtrado": autor_filtrado 
    }
    return render(request, 'DetalleArticulo.html', context)


def posts_por_categoria(request, pk=None):
    categorias_list = Categoria.objects.all()
    
    # Si pk es 0, None o no viene, mostramos todos
    if pk and pk != 0:
        categoria_obj = get_object_or_404(Categoria, pk=pk)
        posts = Post.objects.filter(categoria_post=categoria_obj).order_by('-fecha_creacion')
        activa = pk
    else:
        categoria_obj = {"nombre": "Todos"}
        posts = Post.objects.all().order_by('-fecha_creacion')
        activa = 0

    return render(request, 'categorias.html', {
        'categoria': categoria_obj,
        'categorias_list': categorias_list,
        'posts': posts,
        'categoria_id_activa': activa
    })

def pautas(request):
    
    return render(request,'pautas_Blog.html')

def eventos(request):
   
    return render(request, 'eventos.html', {})

def lista_comentarios_ajax(request, pk):
    #logica igual a detalle_articulo sin el formulario y ni post
    post = get_object_or_404(Post, pk=pk)
    comentarios_qs = post.comentarios.all()
    
    #ordenado por fecha
    orden = request.GET.get('orden', 'mas_nuevo') 
    autor_id_filtro = request.GET.get('autor_id')
    autor_filtrado = None
    
    if orden == 'mas_nuevo':
        comentarios_qs = comentarios_qs.order_by('-fecha_comentario') 
    elif orden == 'mas_antiguo':
        comentarios_qs = comentarios_qs.order_by('fecha_comentario') 

    if autor_id_filtro:
        try:
            autor_filtrado = User.objects.get(id=autor_id_filtro)
            comentarios_qs = comentarios_qs.filter(autor_comentario=autor_filtrado)
        except User.DoesNotExist:
            pass
    html_comentarios = render_to_string(
        'partials/lista_comentarios_fragmento.html',
        {
            'comentarios': comentarios_qs,
            'post': post,
            'orden_actual': orden,
            'autor_filtrado': autor_filtrado
        },
        request=request
    )
    
    return HttpResponse(html_comentarios)


@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_post(request):
    if request.method == 'POST':
        
        form = PostForm(request.POST, request.FILES) 
        
        if form.is_valid():
            nuevo_post = form.save(commit=False)
            try:
                #Obtenemos el perfil de autor vinculado al usuario
                autor_del_usuario = request.user.autor 
            except Autor.DoesNotExist:
                return render(request, 'error.html', {'mensaje': 'Su cuenta no tiene un perfil de autor configurado.'})

            nuevo_post.autor_post = autor_del_usuario

            nuevo_post.save()
            form.save_m2m() 
            # return redirect('detalle_articulo', id_post=nuevo_post.id_post) 
            return redirect('detalle_articulo', pk=nuevo_post.id_post)
    else:
        form = PostForm()
        
    return render(request, 'crear_post.html', {'form': form})

@login_required
def editar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Seguridad: solo el autor puede editar
    if post.autor_post.user != request.user:
        return redirect('home')
    
    if request.method == "POST":
        # Cargamos los datos nuevos sobre la 'instance' del post existente
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detalle_articulo', pk=post.pk)
    else:
        # Cargamos el formulario con los datos actuales del post
        form = PostForm(instance=post)
    
    return render(request, 'editar_post.html', {'form': form, 'post': post})


@login_required
def borrar_post(request, pk):
    # 1. Buscamos el post por su ID (pk)
    post = get_object_or_404(Post, pk=pk)
    
    # 2. Verificamos que el que intenta borrar sea el dueño
    if post.autor_post.user == request.user:
        post.delete()
    
    # 3. Redirigimos al inicio después de borrar
    return redirect('home')

def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email_usuario = request.POST.get('email')
        mensaje = request.POST.get('mensaje')

        # Cuerpo del correo que vas a recibir vos
        cuerpo_mensaje = f"Has recibido un nuevo mensaje de: {nombre}\nCorreo: {email_usuario}\n\nEscribió:\n{mensaje}"

        send_mail(
            f'Mensaje de {nombre}',              # Asunto
            cuerpo_mensaje,                      # Mensaje
            email_usuario,                       # Desde quién (el usuario)
            ['triskelradioonline@gmail.com'],    # A quién (tu correo de la radio)
            fail_silently=False,
        )
        return render(request, 'contacto_exitoso.html') # Una página de "Gracias!"
        
    return render(request, 'contacto.html')