from django.contrib import admin

from .models import Post                        # Esto lo agregue para que funcione el widget
from django.db import models                    # Esto lo agreque para que funcione el widget
from ckeditor.widgets import CKEditorWidget     # Esto lo agreugue para que funcione el widget
from unfold.admin import ModelAdmin             # Esto lo agregue para que funcione el widget

from .models import Post, Categoria, Comentario, Autor

@admin.register(Post)
class PostAdmin(ModelAdmin): 
    
    formfield_overrides = {
        # Esto le dice a Django: para CADA campo que sea TextField en este modelo, 
        # usa el CKEditorWidget en lugar del textarea básico.
        models.TextField: {'widget': CKEditorWidget},
    }
    
class AutorAdmin(admin.ModelAdmin):
    fields=('user', 'nombre', 'email', 'biografia')
    list_display = ("nombre", "email")
    search_fields = ("email",)
    list_filter = ("nombre",)

admin.site.register(Autor, AutorAdmin)
# admin.site.register(Post)             La saco para que funcione el widget!
admin.site.register(Categoria)
admin.site.register(Comentario)
