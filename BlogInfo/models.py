from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import PIL

class Autor(models.Model):
    id_autor=models.BigAutoField(primary_key=True)
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    nombre=models.CharField(max_length=200)
    email=models.EmailField(unique=True)
    biografia=models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id_categoria=models.BigAutoField(primary_key=True)                                  # Agregado
    nombre=models.CharField(max_length=30,default="Sin Nombre")

    def __str__(self):
        return self.nombre

class Post(models.Model):
    id_post=models.BigAutoField(primary_key=True)
    autor_post = models.ForeignKey("Autor", on_delete=models.CASCADE)
    categoria_post = models.ForeignKey("Categoria", on_delete=models.CASCADE, default=1) # Reemplaza '1' con el ID de la categoría por defecto)   # Agregado
    titulo = models.CharField(max_length=200)                                            # Agregadp
    contenido = models.TextField()
    resumen = models.CharField(max_length=400, default="Sin Resumen")                   # Agregado
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    es_destacado = models.BooleanField(default=False)
    link_spotifylist = models.CharField(max_length=200, null=True, blank=True)        # Agregado
    imagen_post = models.ImageField(upload_to='imagenes_post/', null=True, blank=True)  # Agregado


    categorias = models.ManyToManyField(Categoria, related_name="posts", blank=True)

    def __str__(self):
        return self.titulo

    def publicar_articulo(self):
        self.fecha_publicacion = timezone.now
        self.save()

class Comentario(models.Model):
    autor_comentario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido_comentario = models.TextField()
    fecha_comentario = models.DateTimeField(default=timezone.now)
    post=models.ForeignKey(Post, related_name="comentarios", on_delete=models.CASCADE)
    comentario_padre = models.ForeignKey("self", null=True, blank=True, related_name="respuestas", on_delete=models.CASCADE)

    def __str__(self):
        return f"(self.autor_comentario) - (self.contenido_comentario[:30])"
    



