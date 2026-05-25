from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
	avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')

	class Meta:
		verbose_name = 'Профиль'
		verbose_name_plural = 'Профили'

	def __str__(self):
		return self.user.username

	@property
	def avatar_url(self):
		if self.avatar:
			return self.avatar.url
		default_avatars = [
			'img/Kris_sprite.png',
			'img/Susie_sprite.png',
			'img/Ralsei_sprite.png',
			'img/Berdly_sprite.png',
			'img/Noelle_sprite.webp',
			'img/Lancer_sprite.webp',
			'img/Jevil_sprite.webp',
			'img/Spamton_sprite.webp',
			'img/Tenna_sprite.webp',
		]
		index = self.user_id % len(default_avatars) if self.user_id else 0
		return f"{settings.STATIC_URL}{default_avatars[index]}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	"""
	Автоматически создаём Profile при регистрации нового User.
	save_user_profile сигнал не нужен: OneToOneField без auto_now_add
	Не требует дополнительного сохранения при обновлении User.
	"""
	if created:
		Profile.objects.create(user=instance)
