from django.shortcuts import render, get_object_or_404,redirect #luego de hacer comentario para que no de error
from django.http import HttpResponse
from .models import Post
from django.db.models import Count
from .forms import FormularioComentario
from .models import Categoria
from django.template.loader import render_to_string #para mostrar comentarios filtrados sin recargar la pagina
from django.contrib.auth.models import User
from django.utils import timezone

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