import math

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AnswerCreateForm, AnswerVoteForm, CorrectAnswerForm, QuestionCreateForm, QuestionVoteForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .utils import paginate


def _render_questions(request, queryset, template_name, context):
    page = paginate(queryset, request, per_page=10)
    question_liked_ids = []
    question_disliked_ids = []
    if request.user.is_authenticated:
        likes = QuestionLike.objects.filter(user=request.user, question__in=page.object_list).values_list('question_id', 'value')
        question_liked_ids = [question_id for question_id, value in likes if value == 1]
        question_disliked_ids = [question_id for question_id, value in likes if value == -1]

    return render(
        request,
        template_name,
        {
            **context,
            'questions': page.object_list,
            'page_obj': page,
            'question_liked_ids': question_liked_ids,
            'question_disliked_ids': question_disliked_ids,
        },
    )


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

    question_liked_ids = []
    question_disliked_ids = []
    answer_liked_ids = []
    answer_disliked_ids = []
    if request.user.is_authenticated:
        question_likes = QuestionLike.objects.filter(user=request.user, question=question_item).values_list('question_id', 'value')
        question_liked_ids = [question_id for question_id, value in question_likes if value == 1]
        question_disliked_ids = [question_id for question_id, value in question_likes if value == -1]

        answer_likes = AnswerLike.objects.filter(user=request.user, answer__in=answers_page.object_list).values_list('answer_id', 'value')
        answer_liked_ids = [answer_id for answer_id, value in answer_likes if value == 1]
        answer_disliked_ids = [answer_id for answer_id, value in answer_likes if value == -1]
    return render(
        request,
        'questions/question.html',
        {
            'question': question_item,
            'answers': answers_page.object_list,
            'answers_page_obj': answers_page,
            'answer_form': answer_form,
            'question_liked_ids': question_liked_ids,
            'question_disliked_ids': question_disliked_ids,
            'answer_liked_ids': answer_liked_ids,
            'answer_disliked_ids': answer_disliked_ids,
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


@require_POST
def question_vote(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = QuestionVoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'details': form.errors}, status=400)

    question = get_object_or_404(Question, pk=form.cleaned_data['question_id'])
    value = int(form.cleaned_data['value'])

    like = QuestionLike.objects.filter(user=request.user, question=question).first()
    if like:
        if like.value == value:
            return JsonResponse({'error': 'already_voted'}, status=400)
        delta = value - like.value
        like.value = value
        like.save(update_fields=['value'])
    else:
        QuestionLike.objects.create(user=request.user, question=question, value=value)
        delta = value

    Question.objects.filter(pk=question.pk).update(rating=F('rating') + delta)
    question.refresh_from_db(fields=['rating'])
    return JsonResponse({'rating': question.rating})


@require_POST
def answer_vote(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = AnswerVoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'details': form.errors}, status=400)

    answer = get_object_or_404(Answer, pk=form.cleaned_data['answer_id'])
    value = int(form.cleaned_data['value'])

    like = AnswerLike.objects.filter(user=request.user, answer=answer).first()
    if like:
        if like.value == value:
            return JsonResponse({'error': 'already_voted'}, status=400)
        delta = value - like.value
        like.value = value
        like.save(update_fields=['value'])
    else:
        AnswerLike.objects.create(user=request.user, answer=answer, value=value)
        delta = value

    Answer.objects.filter(pk=answer.pk).update(rating=F('rating') + delta)
    answer.refresh_from_db(fields=['rating'])
    return JsonResponse({'rating': answer.rating})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=401)

    form = CorrectAnswerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'details': form.errors}, status=400)

    question = get_object_or_404(Question, pk=form.cleaned_data['question_id'])
    if question.author_id != request.user.id:
        return JsonResponse({'error': 'forbidden'}, status=403)

    answer = get_object_or_404(Answer, pk=form.cleaned_data['answer_id'], question=question)

    with transaction.atomic():
        Answer.objects.filter(question=question, is_correct=True).exclude(pk=answer.pk).update(is_correct=False)
        if not answer.is_correct:
            answer.is_correct = True
            answer.save(update_fields=['is_correct'])

    return JsonResponse({'correct_answer_id': answer.pk})