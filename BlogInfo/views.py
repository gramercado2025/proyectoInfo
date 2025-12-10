from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post
from django.db.models import Count

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

def detalle_articulo(request,pk):
    post = get_object_or_404(Post, pk=pk)
    context = {"post": post}
    #return HttpResponse("Bienvenido a la página prncipal")
    return render(request,'DetalleArticulo.html',context)


