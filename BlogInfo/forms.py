from django import forms
from .models import Comentario # Importa el modelo de Comentario nativo de django

class FormularioComentario(forms.ModelForm):
    # Definimos el campo 'contenido_comentario' para añadirle un widget que hereda de ModelForm
    contenido_comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario aquí...'}),
    )
    
    class Meta:
        model = Comentario
        fields = ('contenido_comentario',)