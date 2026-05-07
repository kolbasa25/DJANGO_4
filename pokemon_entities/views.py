import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    now = localtime()

    for pokemon_entity in PokemonEntity.objects.filter(
        pokemon__image__isnull=False
    ).filter(
        appeared_at__lte=now
    ).filter(
        disappeared_at__gte=now
    ):
        img_url = request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            img_url,
        )

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        img_url = request.build_absolute_uri(pokemon.image.url) if pokemon.image else None
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in pokemon.entities.all():
        add_pokemon(
            folium_map,
            entity.lat,
            entity.lon,
            request.build_absolute_uri(pokemon.image.url) if pokemon.image else None
        )

    pokemon_data = {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else None,
        'entities': [],
    }

    for entity in pokemon.entities.all():
        pokemon_data['entities'].append({
            'level': entity.level,
            'lat': entity.lat,
            'lon': entity.lon,
        })

    if pokemon.previous_evolution:
        prev = pokemon.previous_evolution
        pokemon_data['previous_evolution'] = {
            'title_ru': prev.title,
            'pokemon_id': prev.id,
            'img_url': request.build_absolute_uri(prev.image.url) if prev.image else None,
        }

    next_evo = pokemon.next_evolutions.first()
    if next_evo:
        pokemon_data['next_evolution'] = {
            'title_ru': next_evo.title,
            'pokemon_id': next_evo.id,
            'img_url': request.build_absolute_uri(next_evo.image.url) if next_evo.image else None,
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data,
    })