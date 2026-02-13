
import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import Gallery, GalleryAlbum
from django.core.files import File

# Removed Faker dependency for simplicity
# fake = Faker()

def create_albums():
    albums_data = [
        {
            'title_fr': 'Rentrée Solennelle 2024',
            'description_fr': 'Cérémonie d\'accueil des nouveaux étudiants.',
            'date': '2024-10-15'
        },
        {
            'title_fr': 'Hackathon COMS.A.S 2024',
            'description_fr': 'Un marathon de programmation de 48h.',
            'date': '2024-11-20'
        },
        {
            'title_fr': 'Soirée de Gala',
            'description_fr': 'Soirée de clôture de l\'année académique.',
            'date': '2025-06-30'
        }
    ]

    created_albums = []
    for data in albums_data:
        album, created = GalleryAlbum.objects.get_or_create(
            title_fr=data['title_fr'],
            defaults={
                'description_fr': data['description_fr'],
                'event_date': data['date']
            }
        )
        if created:
            print(f"Created album: {album.title_fr}")
        else:
            print(f"Album exists: {album.title_fr}")
        created_albums.append(album)
    return created_albums

def assign_images_to_albums(albums):
    images = Gallery.objects.filter(media_type='image', album__isnull=True)
    count = images.count()
    print(f"Found {count} unassigned images.")
    
    if count == 0:
        print("Creating dummy images...")
        # create dummy images if none exist
        for i in range(12):
            album = random.choice(albums)
            Gallery.objects.create(
                title_fr=f"Photo {i+1}",
                description_fr="Une belle photo souvenir de l'événement.",
                media_type='image',
                album=album,
                is_featured=random.bool()
            )
            print(f"Created dummy image attached to {album.title_fr}")
    else:
        for image in images:
            album = random.choice(albums)
            image.album = album
            image.save()
            print(f"Assigned image '{image.title_fr}' to '{album.title_fr}'")

if __name__ == '__main__':
    albums = create_albums()
    assign_images_to_albums(albums)
    print("Gallery population complete.")
