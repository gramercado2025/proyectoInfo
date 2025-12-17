from django import forms
from django.shortcuts import render,redirect
from .models import Comentario # Importa el modelo de Comentario nativo de django
from .models import Post, Categoria, Autor, Comentario

from .models import Post, Categoria, Autor, Comentario 

# 🚨 DEFINICIÓN DE POSTFORM - DEBE ESTAR AQUÍ 🚨
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'titulo', 
            'contenido', 
            'resumen', 
            'categoria_post', 
            'link_spotifylist', 
            'imagen_post',
        ]
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 15}),
            'resumen': forms.Textarea(attrs={'rows': 4}),
        }

class FormularioComentario(forms.ModelForm):
    # Definimos el campo 'contenido_comentario' para añadirle un widget que hereda de ModelForm
    contenido_comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario aquí...'}),
    )
    
    class Meta:
        model = Comentario
        fields = ('contenido_comentario',)


