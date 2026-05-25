import math

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerCreateForm, QuestionCreateForm
from .models import Question, Tag
from .utils import paginate


def _render_questions(request, queryset, template_name, context):
    page = paginate(queryset, request, per_page=10)
    popular_tags = Tag.objects.all()[:10]
    return render(request, template_name, {**context, 'questions': page.object_list, 'page_obj': page, 'popular_tags': popular_tags})


def index(request):
    return _render_questions(request, Question.objects.new(), 'questions/index.html', {'page_title': 'New Questions'})


def hot(request):
    return _render_questions(request, Question.objects.hot(), 'questions/hot.html', {'page_title': 'Hot Questions'})


def tag(request, tag):
    selected_tag = get_object_or_404(Tag, slug__iexact=tag)
    return _render_questions(
        request,
        Question.objects.by_tag(selected_tag.slug),
        'questions/tag.html',
        {'selected_tag': selected_tag.slug},
    )


def question(request, id):
    question_item = get_object_or_404(Question.objects.new(), pk=id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        answer_form = AnswerCreateForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(author=request.user, question=question_item)
            answers_count = question_item.answers.count()
            page_number = max(1, math.ceil(answers_count / 10))
            redirect_url = f'{question_item.get_absolute_url()}?page={page_number}#answer-{answer.pk}'
            return redirect(redirect_url)
    else:
        answer_form = AnswerCreateForm()

    answers_page = paginate(question_item.answers.select_related('author', 'author__profile'), request, per_page=10)
    return render(
        request,
        'questions/question.html',
        {
            'question': question_item,
            'answers': answers_page.object_list,
            'answers_page_obj': answers_page,
            'answer_form': answer_form,
        },
    )


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionCreateForm(request.POST)
        if form.is_valid():
            question_item = form.save(author=request.user)
            return redirect(question_item.get_absolute_url())
    else:
        form = QuestionCreateForm()

    return render(request, 'questions/ask.html', {'form': form})