from django.contrib import admin
from .models import Question, Answer, Tag, QuestionLike, AnswerLike


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    raw_id_fields = ('author',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    fieldsets = (
        ('Основное', {'fields': ('name',)}),
        ('Описание', {'fields': ('description',)}),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'get_likes_count', 'get_answers_count')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'text', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    raw_id_fields = ('author',)
    inlines = (AnswerInline,)
    fieldsets = (
        ('Основное', {'fields': ('title', 'author', 'text')}),
        ('Теги', {'fields': ('tags',)}),
        ('Даты', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Лайки'

    def get_answers_count(self, obj):
        return obj.answers.count()
    get_answers_count.short_description = 'Ответы'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related('tags', 'likes', 'answers')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('get_question_title', 'author', 'created_at', 'get_likes_count')
    list_filter = ('created_at', 'question')
    search_fields = ('text', 'author__username', 'question__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('question', 'author')
    fieldsets = (
        ('Основное', {'fields': ('question', 'author', 'text')}),
        ('Даты', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_question_title(self, obj):
        return obj.question.title
    get_question_title.short_description = 'Вопрос'

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Лайки'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('question', 'author')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_question_title', 'created_at')
    list_filter = ('created_at', 'question')
    search_fields = ('user__username', 'question__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'question')
    fieldsets = (
        ('Основное', {'fields': ('user', 'question')}),
        ('Дата', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def get_question_title(self, obj):
        return obj.question.title
    get_question_title.short_description = 'Вопрос'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_answer_id', 'get_question_title', 'created_at')
    list_filter = ('created_at', 'answer__question')
    search_fields = ('user__username', 'answer__question__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'answer')
    fieldsets = (
        ('Основное', {'fields': ('user', 'answer')}),
        ('Дата', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def get_answer_id(self, obj):
        return f'Ответ #{obj.answer.id}'
    get_answer_id.short_description = 'Ответ'

    def get_question_title(self, obj):
        return obj.answer.question.title
    get_question_title.short_description = 'Вопрос'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'answer', 'answer__question')
