from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class QuestionQuerySet(models.QuerySet):
	def with_related(self):
		return self.select_related('author', 'author__profile').prefetch_related('tags')

	def with_answers_count(self):
		return self.annotate(answers_count=Count('answers', distinct=True))

	def new(self):
		return self.with_related().with_answers_count().order_by('-created_at')

	def hot(self):
		return self.with_related().with_answers_count().order_by('-rating', '-created_at')

	def by_tag(self, tag_name):
		return self.filter(tags__name__iexact=tag_name).new()


class QuestionManager(models.Manager):
	def get_queryset(self):
		return QuestionQuerySet(self.model, using=self._db)

	def new(self):
		return self.get_queryset().new()

	def hot(self):
		return self.get_queryset().hot()

	def by_tag(self, tag_name):
		return self.get_queryset().by_tag(tag_name)


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
	avatar = models.CharField(max_length=255, blank=True, default='img/Kris_sprite.png', verbose_name='Путь к аватару')

	class Meta:
		verbose_name = 'Профиль'
		verbose_name_plural = 'Профили'

	def __str__(self):
		return self.user.username


class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='Название')

	class Meta:
		verbose_name = 'Тег'
		verbose_name_plural = 'Теги'

	def __str__(self):
		return self.name


class Question(models.Model):
	title = models.CharField(max_length=255, verbose_name='Заголовок')
	text = models.TextField(verbose_name='Текст')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
	tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги')
	rating = models.IntegerField(default=0, db_index=True, verbose_name='Рейтинг')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')

	objects = QuestionManager()

	class Meta:
		verbose_name = 'Вопрос'
		verbose_name_plural = 'Вопросы'
		ordering = ['-created_at']

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('question', kwargs={'id': self.pk})


class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
	text = models.TextField(verbose_name='Текст')
	rating = models.IntegerField(default=0, db_index=True, verbose_name='Рейтинг')
	is_correct = models.BooleanField(default=False, verbose_name='Правильный')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')

	class Meta:
		verbose_name = 'Ответ'
		verbose_name_plural = 'Ответы'
		ordering = ['created_at']

	def __str__(self):
		return f'Answer #{self.pk} to question #{self.question_id}'


class QuestionLike(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes', verbose_name='Пользователь')
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')
	value = models.SmallIntegerField(default=1, verbose_name='Значение')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	class Meta:
		verbose_name = 'Лайк вопроса'
		verbose_name_plural = 'Лайки вопросов'
		constraints = [
			models.UniqueConstraint(fields=['user', 'question'], name='unique_user_question_like'),
		]

	def __str__(self):
		return f'{self.user_id} -> Q{self.question_id}'


class AnswerLike(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes', verbose_name='Пользователь')
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')
	value = models.SmallIntegerField(default=1, verbose_name='Значение')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	class Meta:
		verbose_name = 'Лайк ответа'
		verbose_name_plural = 'Лайки ответов'
		constraints = [
			models.UniqueConstraint(fields=['user', 'answer'], name='unique_user_answer_like'),
		]

	def __str__(self):
		return f'{self.user_id} -> A{self.answer_id}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	if hasattr(instance, 'profile'):
		instance.profile.save()
