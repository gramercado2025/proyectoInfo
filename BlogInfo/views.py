from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post
from django.core.paginator import Paginator # Para la paginacion
from django.db.models import Count
from .forms import FormularioComentario
from .models import Post, Comentario # Necesito Post y Comentario
from .models import Categoria
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

# Antigua vista de la pagina principal sin paginación, la comento por las dudas
#def home(request):
    
#    post_destacado = Post.objects.filter(es_destacado=True).annotate(total_comentarios=Count('comentarios')).first()
#    posts= Post.objects.annotate(total_comentarios=Count('comentarios')).order_by("fecha_creacion")
#    if post_destacado:
#        posts = posts.exclude(id_post=post_destacado.id_post)
#    context = {"posts": posts, "post_destacado":post_destacado}
#
#    return render(request,'index_final.html',context)

# views.py

def home(request):
    
    # 1. Obtener y preparar el Post Destacado
    post_destacado = Post.objects.filter(es_destacado=True).annotate(total_comentarios=Count('comentarios')).first()
    
    # 2. Obtener la lista BASE de Posts a paginar (ordenada)
    posts_list = Post.objects.annotate(total_comentarios=Count('comentarios')).order_by("fecha_creacion")
    
    # 3. Excluir el post destacado
    if post_destacado:
        posts_list = posts_list.exclude(id_post=post_destacado.id_post)

    # 4. Configurar el Paginator (4 posts por página)
    posts_por_pagina = 4 
    paginator = Paginator(posts_list, posts_por_pagina)
    
    # 5. Obtener el número de página de la URL (?page=X)
    page_number = request.GET.get('page')
    
    # 6. Obtener el objeto Page para la página solicitada
    page_obj = paginator.get_page(page_number)
    
    # 7. Renderizar el template
    context = {
        "page_obj": page_obj, 
        "post_destacado": post_destacado
    }

    return render(request, 'index_final.html', context)

def detalle_articulo(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comentarios = post.comentarios.all().order_by('-fecha_comentario') 
    if request.method == 'POST':
        form = FormularioComentario(request.POST)
        
        if not request.user.is_authenticated: #Verificar que el usuario esté logueado antes de procesar
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
        "comentarios": comentarios,        
        "form_comentario": form,           
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

def pautas(request):
    
    return render(request,'pautas_Blog.html')

def eventos(request):
   
    return render(request, 'eventos.html', {})
