from django.core.management.base import BaseCommand
from apps.curtains.models import Curtain
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Bo\'sh slug maydonlarini tuzatish'

    def handle(self, *args, **options):
        self.stdout.write('Slug maydonlarini tekshirish va tuzatish...')
        
        curtains_fixed = 0
        
        for curtain in Curtain.objects.all():
            if not curtain.slug or curtain.slug.strip() == '':
                # Slug yaratish
                new_slug = slugify(curtain.title)
                
                # Slug unique emasligini tekshirish
                original_slug = new_slug
                counter = 1
                while Curtain.objects.filter(slug=new_slug).exclude(id=curtain.id).exists():
                    new_slug = f'{original_slug}-{counter}'
                    counter += 1
                
                # Slug yangilash
                curtain.slug = new_slug
                curtain.save(update_fields=['slug'])
                
                self.stdout.write(f'Tuzatildi: "{curtain.title}" -> "{new_slug}"')
                curtains_fixed += 1
            else:
                self.stdout.write(f'OK: "{curtain.title}" -> "{curtain.slug}"')
        
        if curtains_fixed > 0:
            self.stdout.write(
                self.style.SUCCESS(f'{curtains_fixed} ta parda slug maydonlari tuzatildi!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Barcha slug maydonlari to\'g\'ri!')
            )