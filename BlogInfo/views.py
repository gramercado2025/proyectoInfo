from django.shortcuts import render, get_object_or_404,redirect #luego de hacer comentario para que no de error
from django.http import HttpResponse
from .models import Post, Autor
from django.db.models import Count
from .forms import FormularioComentario, PostForm
from .models import Categoria
from django.template.loader import render_to_string #para mostrar comentarios filtrados sin recargar la pagina
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def home(request):
    
    # --- 1. Obtener parámetros de ordenación y búsqueda ---
    orden = request.GET.get('order_by', 'reciente') 
    search_term = request.GET.get('q')

    # --- 2. Post Destacado ---
    # Lo obtenemos y anotamos aparte, ya que lo excluiremos de la lista principal.
    post_destacado = Post.objects.filter(es_destacado=True).annotate(
        total_comentarios=Count('comentarios')
    ).first()
    
    # --- 3. Definición BASE de la lista de Posts (IMPORTANTE: Se define SIEMPRE) ---
    # Usaremos 'posts' como nuestra variable principal para la consulta.
    posts = Post.objects.all().annotate(total_comentarios=Count('comentarios'))

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
        posts = posts.exclude(id=post_destacado.id) # Usa 'id' si ese es el nombre de tu PK
        
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


        

    


def pautas(request):
    #return HttpResponse("Bienvenido a la página prncipal")
    return render(request,'pautas_Blog.html')

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


def lista_categorias_general(request):
    
    categorias_con_conteo = Categoria.objects.annotate(
        num_posts=Count('post') 
    ).order_by('nombre')
    
    context = {
        "categorias_list": categorias_con_conteo 
    }
    
    return render(request, 'listado_categorias.html', context)

def posts_por_categoria(request, pk):
    
    categoria = get_object_or_404(Categoria, pk=pk)
    posts = Post.objects.filter(categoria_post=categoria).order_by('-fecha_creacion')
    context = {
        "categoria": categoria, 
        "posts": posts,         
    }
    return render(request, 'categorias.html', context)

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
def crear_post(request):
    if request.method == 'POST':
        
        form = PostForm(request.POST, request.FILES) 
        
        if form.is_valid():
            nuevo_post = form.save(commit=False)
            try:
                autor_del_usuario = request.user.autor 
            except Autor.DoesNotExist:
                return render(request, 'error.html', {'mensaje': 'Su cuenta no tiene un perfil de autor configurado.'})

            nuevo_post.autor_post = autor_del_usuario
            nuevo_post.save()
            form.save_m2m() 
            return redirect('detalle_articulo', id_post=nuevo_post.id_post) 
    else:
        form = PostForm()
        
    return render(request, 'crear_post.html', {'form': form})