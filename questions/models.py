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
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='User')
	avatar = models.CharField(max_length=255, blank=True, default='img/Kris_sprite.png', verbose_name='Avatar path')

	class Meta:
		verbose_name = 'Profile'
		verbose_name_plural = 'Profiles'

	def __str__(self):
		return self.user.username


class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='Name')

	class Meta:
		verbose_name = 'Tag'
		verbose_name_plural = 'Tags'

	def __str__(self):
		return self.name


class Question(models.Model):
	title = models.CharField(max_length=255, verbose_name='Title')
	text = models.TextField(verbose_name='Text')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Author')
	tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Tags')
	rating = models.IntegerField(default=0, db_index=True, verbose_name='Rating')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created at')

	objects = QuestionManager()

	class Meta:
		verbose_name = 'Question'
		verbose_name_plural = 'Questions'
		ordering = ['-created_at']

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('question', kwargs={'id': self.pk})


class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Question')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Author')
	text = models.TextField(verbose_name='Text')
	rating = models.IntegerField(default=0, db_index=True, verbose_name='Rating')
	is_correct = models.BooleanField(default=False, verbose_name='Is correct')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created at')

	class Meta:
		verbose_name = 'Answer'
		verbose_name_plural = 'Answers'
		ordering = ['created_at']

	def __str__(self):
		return f'Answer #{self.pk} to question #{self.question_id}'


class QuestionLike(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes', verbose_name='User')
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Question')
	value = models.SmallIntegerField(default=1, verbose_name='Value')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

	class Meta:
		verbose_name = 'Question like'
		verbose_name_plural = 'Question likes'
		constraints = [
			models.UniqueConstraint(fields=['user', 'question'], name='unique_user_question_like'),
		]

	def __str__(self):
		return f'{self.user_id} -> Q{self.question_id}'


class AnswerLike(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes', verbose_name='User')
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Answer')
	value = models.SmallIntegerField(default=1, verbose_name='Value')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

	class Meta:
		verbose_name = 'Answer like'
		verbose_name_plural = 'Answer likes'
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
