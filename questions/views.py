from django.http import Http404
from django.shortcuts import render

from .utils import paginate


def _build_questions():
    questions = [
        {
            'id': 1,
            'title': 'How to open a Snowgrave way in Deltarune?',
            'text': "I am trying to open the Snowgrave way in Deltarune, but I can't figure out how to do it. Can someone help me with this?",
            'tags': ['deltarune', 'snowgrave'],
            'answers_count': 5,
            'votes': 10,
            'author': 'Spamton',
            'avatar': 'img/Spamton_sprite.webp',
        },
        {
            'id': 2,
            'title': 'What are the best strategies for beating King in Deltarune?',
            'text': 'I keep losing to King in Deltarune battles. What are some effective strategies and team compositions I should use?',
            'tags': ['deltarune', 'combat'],
            'answers_count': 8,
            'votes': 15,
            'author': 'Kris',
            'avatar': 'img/Kris_sprite.png',
        },
        {
            'id': 3,
            'title': 'How can I unlock all secret areas in Deltarune?',
            'text': 'I want to find and unlock all the secret areas and Easter eggs in Deltarune. Where should I look and what do I need to do?',
            'tags': ['deltarune', 'secrets'],
            'answers_count': 12,
            'votes': 18,
            'author': 'Tenna',
            'avatar': 'img/Tenna_overworld_putting_his_hands_up.webp',
        },
    ]

    tags_cycle = [
        ('deltarune', 'chapter1'),
        ('deltarune', 'chapter2'),
        ('deltarune', 'lore'),
        ('deltarune', 'boss'),
        ('deltarune', 'build'),
    ]
    avatars = [
        'img/Spamton_sprite.webp',
        'img/Kris_sprite.png',
        'img/Ralsei_sprite.png',
        'img/Noelle_sprite.webp',
        'img/Berdly_sprite.png',
    ]

    for i in range(4, 31):
        first_tag, second_tag = tags_cycle[i % len(tags_cycle)]
        questions.append(
            {
                'id': i,
                'title': f'Question #{i}',
                'text': "question's text",
                'tags': [first_tag, second_tag],
                'answers_count': (i % 7) + 1,
                'votes': (i * 3) % 25,
                'author': f'User{i}',
                'avatar': avatars[i % len(avatars)],
            }
        )

    return questions


QUESTIONS = _build_questions()

def index(request):
    ordered = sorted(QUESTIONS, key=lambda question: question['id'], reverse=True)
    page = paginate(ordered, request, per_page=10)
    return render(
        request,
        'questions/index.html',
        {
            'page_title': 'New Questions',
            'questions': page.object_list,
            'page_obj': page,
        },
    )


def hot(request):
    ordered = sorted(QUESTIONS, key=lambda question: question['votes'], reverse=True)
    page = paginate(ordered, request, per_page=10)
    return render(
        request,
        'questions/hot.html',
        {
            'page_title': 'Hot Questions',
            'questions': page.object_list,
            'page_obj': page,
        },
    )


def tag(request, tag):
    normalized_tag = tag.lower()
    filtered = [
        question
        for question in QUESTIONS
        if normalized_tag in [item.lower() for item in question['tags']]
    ]
    page = paginate(filtered, request, per_page=10)
    return render(
        request,
        'questions/tag.html',
        {
            'selected_tag': tag,
            'questions': page.object_list,
            'page_obj': page,
        },
    )


def question(request, id):
    question_item = next((item for item in QUESTIONS if item['id'] == id), None)
    if question_item is None:
        raise Http404('Question not found')

    answers = [
        {
            'author': 'Ralsei',
            'text': 'Try checking dialogue branches and make sure you complete all required actions in chapter order.',
            'votes': 7,
            'is_correct': True,
            'avatar': 'img/Ralsei_sprite.png',
        },
        {
            'author': 'Susie',
            'text': 'I usually brute-force all encounters first, then revisit choices. Works surprisingly often.',
            'votes': 4,
            'is_correct': False,
            'avatar': 'img/Kris_sprite.png',
        },
        {
            'author': 'Noelle',
            'text': 'A walkthrough can help if you are stuck, but keep backups of save files before risky choices.',
            'votes': 5,
            'is_correct': False,
            'avatar': 'img/Noelle_sprite.webp',
        },
    ]

    return render(
        request,
        'questions/question.html',
        {
            'question': question_item,
            'answers': answers,
        },
    )


def ask(request):
    return render(request, 'questions/ask.html')