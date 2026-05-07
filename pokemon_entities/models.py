from django.db import models


class Pokemon(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    title_en = models.CharField(
        max_length=200, blank=True, verbose_name='Название на английском'
    )
    title_jp = models.CharField(
        max_length=200, blank=True, verbose_name='Название на японском'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(
        upload_to='pokemon_images',
        null=True,
        blank=True,
        verbose_name='Изображение',
    )
    previous_evolution = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_evolutions',
        verbose_name='Из кого эволюционировал',
    )

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='entities',
        verbose_name='Покемон',
    )
    lat = models.FloatField(verbose_name='Широта')
    lon = models.FloatField(verbose_name='Долгота')
    appeared_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Появится'
    )
    disappeared_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Исчезнет'
    )
    level = models.IntegerField(
        null=True, blank=True, verbose_name='Уровень'
    )
    health = models.IntegerField(
        null=True, blank=True, verbose_name='Здоровье'
    )
    strength = models.IntegerField(
        null=True, blank=True, verbose_name='Атака'
    )
    defence = models.IntegerField(
        null=True, blank=True, verbose_name='Защита'
    )
    stamina = models.IntegerField(
        null=True, blank=True, verbose_name='Выносливость'
    )

    def __str__(self):
        return f'{self.pokemon} ({self.lat}, {self.lon})'