from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


from core.models import Profile


class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	extra = 0
	fk_name = 'user'


class CustomUserAdmin(UserAdmin):
	inlines = [ProfileInline]
	list_select_related = ('profile',)


class AnswerInline(admin.TabularInline):
	model = Answer
	extra = 0
	raw_id_fields = ('author',)
	fields = ('author', 'text', 'rating', 'is_correct', 'created_at')
	readonly_fields = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('id', 'slug')
	list_filter = ('slug',)
	search_fields = ('slug',)
	ordering = ('slug',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'author', 'rating', 'created_at')
	list_filter = ('created_at', 'tags')
	search_fields = ('title', 'text', 'author__username')
	raw_id_fields = ('author',)
	autocomplete_fields = ('tags',)
	inlines = [AnswerInline]

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('author').prefetch_related('tags')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_display = ('id', 'question', 'author', 'rating', 'is_correct', 'created_at')
	list_filter = ('is_correct', 'created_at')
	search_fields = ('text', 'author__username', 'question__title')
	raw_id_fields = ('question', 'author')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('question', 'author')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'question', 'value', 'created_at')
	list_filter = ('value', 'created_at')
	search_fields = ('user__username', 'question__title')
	raw_id_fields = ('user', 'question')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'answer', 'value', 'created_at')
	list_filter = ('value', 'created_at')
	search_fields = ('user__username', 'answer__text')
	raw_id_fields = ('user', 'answer')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user', 'answer')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
