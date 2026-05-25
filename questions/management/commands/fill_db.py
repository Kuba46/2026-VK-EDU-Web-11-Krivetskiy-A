import random
from time import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


class Command(BaseCommand):
    help = 'Fill database with test data: python manage.py fill_db [ratio]'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=100)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio <= 0:
            raise CommandError('ratio must be a positive integer')

        faker = Faker()
        random.seed()

        users_to_create = ratio
        tags_to_create = ratio
        questions_to_create = ratio * 10
        answers_to_create = ratio * 100
        likes_to_create = ratio * 200

        start_time = int(time())
        users_prefix = f'fill{start_time}_u_'
        tags_prefix = f'fill{start_time}_t_'
        questions_prefix = f'fill{start_time}_q_'
        answers_prefix = f'fill{start_time}_a_'

        self.stdout.write(self.style.NOTICE(f'Creating users: {users_to_create}'))
        self._create_users(faker, users_to_create, users_prefix)

        self.stdout.write(self.style.NOTICE(f'Creating tags: {tags_to_create}'))
        self._create_tags(faker, tags_to_create, tags_prefix)

        user_ids = list(User.objects.values_list('id', flat=True))
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        self.stdout.write(self.style.NOTICE(f'Creating questions: {questions_to_create}'))
        self._create_questions_with_tags(faker, questions_to_create, questions_prefix, user_ids, tag_ids)

        question_ids = list(Question.objects.values_list('id', flat=True))

        self.stdout.write(self.style.NOTICE(f'Creating answers: {answers_to_create}'))
        self._create_answers(faker, answers_to_create, answers_prefix, user_ids, question_ids)

        answer_ids = list(Answer.objects.values_list('id', flat=True))

        self.stdout.write(self.style.NOTICE(f'Creating likes: {likes_to_create}'))
        self._create_likes(likes_to_create, user_ids, question_ids, answer_ids)
        self._recalculate_ratings()

        self.stdout.write(self.style.SUCCESS('Database has been successfully filled.'))

    def _create_users(self, faker, amount, prefix, batch_size=5000):
        batch = []
        for index in range(amount):
            username = f'{prefix}{index}'
            batch.append(
                User(
                    username=username,
                    email=f'{username}@example.com',
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                )
            )
            if len(batch) >= batch_size:
                User.objects.bulk_create(batch, batch_size=batch_size)
                batch.clear()

        if batch:
            User.objects.bulk_create(batch, batch_size=batch_size)

        new_user_ids = list(User.objects.filter(username__startswith=prefix).values_list('id', flat=True))
        profile_batch = [Profile(user_id=user_id) for user_id in new_user_ids]
        Profile.objects.bulk_create(profile_batch, batch_size=batch_size, ignore_conflicts=True)

    def _create_tags(self, faker, amount, prefix, batch_size=5000):
        batch = []
        for index in range(amount):
            tag_name = f'{prefix}{index}_{faker.word()}'
            batch.append(Tag(name=tag_name[:64]))
            if len(batch) >= batch_size:
                Tag.objects.bulk_create(batch, batch_size=batch_size, ignore_conflicts=True)
                batch.clear()

        if batch:
            Tag.objects.bulk_create(batch, batch_size=batch_size, ignore_conflicts=True)

    def _create_questions_with_tags(self, faker, amount, prefix, user_ids, tag_ids, batch_size=5000):
        if not user_ids or not tag_ids:
            raise CommandError('Cannot create questions without users and tags')

        created_question_ids = []
        batch = []
        for index in range(amount):
            title = f'{prefix}{index} {faker.sentence(nb_words=6)}'[:255]
            batch.append(
                Question(
                    title=title,
                    text=faker.text(max_nb_chars=600),
                    author_id=random.choice(user_ids),
                    rating=random.randint(-10, 250),
                )
            )
            if len(batch) >= batch_size:
                created = Question.objects.bulk_create(batch, batch_size=batch_size)
                created_question_ids.extend(question.id for question in created)
                batch.clear()

        if batch:
            created = Question.objects.bulk_create(batch, batch_size=batch_size)
            created_question_ids.extend(question.id for question in created)

        if not created_question_ids:
            created_question_ids = list(Question.objects.filter(title__startswith=prefix).values_list('id', flat=True))

        through_model = Question.tags.through
        links_batch = []
        for question_id in created_question_ids:
            selected = random.sample(tag_ids, 2 if len(tag_ids) >= 2 else 1)
            for tag_id in selected:
                links_batch.append(through_model(question_id=question_id, tag_id=tag_id))
            if len(links_batch) >= batch_size:
                through_model.objects.bulk_create(links_batch, batch_size=batch_size, ignore_conflicts=True)
                links_batch.clear()

        if links_batch:
            through_model.objects.bulk_create(links_batch, batch_size=batch_size, ignore_conflicts=True)

    def _create_answers(self, faker, amount, prefix, user_ids, question_ids, batch_size=5000):
        if not user_ids or not question_ids:
            raise CommandError('Cannot create answers without users and questions')

        batch = []
        for index in range(amount):
            text = f'{prefix}{index} {faker.text(max_nb_chars=400)}'
            batch.append(
                Answer(
                    question_id=random.choice(question_ids),
                    author_id=random.choice(user_ids),
                    text=text,
                    rating=random.randint(-5, 120),
                    is_correct=index % 25 == 0,
                )
            )
            if len(batch) >= batch_size:
                Answer.objects.bulk_create(batch, batch_size=batch_size)
                batch.clear()

        if batch:
            Answer.objects.bulk_create(batch, batch_size=batch_size)

    def _create_likes(self, amount, user_ids, question_ids, answer_ids, batch_size=10000):
        if not user_ids or not question_ids or not answer_ids:
            raise CommandError('Cannot create likes without users, questions and answers')

        users_count = len(user_ids)
        questions_count = len(question_ids)
        answers_count = len(answer_ids)

        question_likes_target = amount // 2
        answer_likes_target = amount - question_likes_target

        question_likes_batch = []
        for index in range(question_likes_target):
            question_likes_batch.append(
                QuestionLike(
                    user_id=user_ids[index % users_count],
                    question_id=question_ids[(index // users_count) % questions_count],
                    value=1 if index % 2 == 0 else -1,
                )
            )
            if len(question_likes_batch) >= batch_size:
                QuestionLike.objects.bulk_create(question_likes_batch, batch_size=batch_size, ignore_conflicts=True)
                question_likes_batch.clear()

        if question_likes_batch:
            QuestionLike.objects.bulk_create(question_likes_batch, batch_size=batch_size, ignore_conflicts=True)

        answer_likes_batch = []
        for index in range(answer_likes_target):
            answer_likes_batch.append(
                AnswerLike(
                    user_id=user_ids[index % users_count],
                    answer_id=answer_ids[(index // users_count) % answers_count],
                    value=1 if index % 2 == 0 else -1,
                )
            )
            if len(answer_likes_batch) >= batch_size:
                AnswerLike.objects.bulk_create(answer_likes_batch, batch_size=batch_size, ignore_conflicts=True)
                answer_likes_batch.clear()

        if answer_likes_batch:
            AnswerLike.objects.bulk_create(answer_likes_batch, batch_size=batch_size, ignore_conflicts=True)

    def _recalculate_ratings(self, batch_size=5000):
        question_totals = QuestionLike.objects.values('question_id').annotate(total=Sum('value'))
        question_map = {row['question_id']: row['total'] or 0 for row in question_totals}
        question_ids = list(question_map.keys())
        for start in range(0, len(question_ids), batch_size):
            chunk_ids = question_ids[start:start + batch_size]
            questions = list(Question.objects.filter(id__in=chunk_ids))
            for question in questions:
                question.rating = question_map.get(question.id, 0)
            Question.objects.bulk_update(questions, ['rating'], batch_size=batch_size)

        answer_totals = AnswerLike.objects.values('answer_id').annotate(total=Sum('value'))
        answer_map = {row['answer_id']: row['total'] or 0 for row in answer_totals}
        answer_ids = list(answer_map.keys())
        for start in range(0, len(answer_ids), batch_size):
            chunk_ids = answer_ids[start:start + batch_size]
            answers = list(Answer.objects.filter(id__in=chunk_ids))
            for answer in answers:
                answer.rating = answer_map.get(answer.id, 0)
            Answer.objects.bulk_update(answers, ['rating'], batch_size=batch_size)
