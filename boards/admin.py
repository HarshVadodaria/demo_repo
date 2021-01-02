from django.contrib import admin
from .models import Board , Topic , Post
from django.contrib import messages
# Register your models here.

class BoardAdmin(admin.ModelAdmin):
	fieldsets = (
		('standard Information:', {
			'fields' : ('name', )
		}),
		('Description Information', {
			'fields' : ('description', )
		}),
	) 
	

	list_display = ('name', 'description')
	list_filter = ('name', )
	search_fields = ("name__startswith", )

	def null_des(modeladmin, request, queryset):
		queryset.update(description = '')
		messages.success(request, "Description is removed!!!")
	admin.site.add_action(null_des, "Remove Description.")	

# admin.site.unregister(Board)
# admin.site.register(Board)
admin.site.register(Board, BoardAdmin)
admin.site.register(Topic)
admin.site.register(Post)