from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'avatar')
	list_filter = ('avatar',)
	search_fields = ('user__username',)
	raw_id_fields = ('user',)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user')
