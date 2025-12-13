from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post
from django.db.models import Count
from .forms import FormularioComentario
from .models import Post, Comentario # Necesitas Post y Comentario
from .models import Categoria
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
def home(request):
    
    post_destacado = Post.objects.filter(es_destacado=True).annotate(total_comentarios=Count('comentarios')).first()
    posts= Post.objects.annotate(total_comentarios=Count('comentarios')).order_by("fecha_creacion")
    if post_destacado:
        posts = posts.exclude(id_post=post_destacado.id_post)
    context = {"posts": posts, "post_destacado":post_destacado}

    return render(request,'index_final.html',context)


def pautas(request):
    #return HttpResponse("Bienvenido a la página prncipal")
    return render(request,'pautas_Blog.html')

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


