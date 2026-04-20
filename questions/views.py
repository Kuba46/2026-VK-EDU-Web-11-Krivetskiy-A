from django.shortcuts import get_object_or_404, render

from .models import Question, Tag
from .utils import paginate


def _render_questions(request, queryset, template_name, context):
    page = paginate(queryset, request, per_page=10)
    return render(request, template_name, {**context, 'questions': page.object_list, 'page_obj': page})


def index(request):
    return _render_questions(request, Question.objects.new(), 'questions/index.html', {'page_title': 'New Questions'})


def hot(request):
    return _render_questions(request, Question.objects.hot(), 'questions/hot.html', {'page_title': 'Hot Questions'})


def tag(request, tag):
    selected_tag = get_object_or_404(Tag, name__iexact=tag)
    return _render_questions(
        request,
        Question.objects.by_tag(selected_tag.name),
        'questions/tag.html',
        {'selected_tag': selected_tag.name},
    )


def question(request, id):
    question_item = get_object_or_404(Question.objects.new(), pk=id)
    answers_page = paginate(question_item.answers.select_related('author', 'author__profile'), request, per_page=10)
    return render(
        request,
        'questions/question.html',
        {'question': question_item, 'answers': answers_page.object_list, 'answers_page_obj': answers_page},
    )


def ask(request):
    return render(request, 'questions/ask.html')