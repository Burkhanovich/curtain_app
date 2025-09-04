from django.core.management.base import BaseCommand
from apps.curtains.models import Curtain, CurtainImage
from PIL import Image, ImageDraw
import os
from io import BytesIO
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Har bir parda uchun demo rasmlar yaratish'

    def handle(self, *args, **options):
        self.stdout.write('Parda rasmlarini yaratish boshlandi...')
        
        # Rang palitralari
        color_schemes = {
            'klassik': [(139, 69, 19), (160, 82, 45), (205, 133, 63)],
            'zamonaviy': [(220, 220, 220), (192, 192, 192), (169, 169, 169)],
            'hashamatli': [(218, 165, 32), (255, 215, 0), (255, 248, 220)],
            'bolalar': [(255, 182, 193), (255, 228, 225), (255, 240, 245)],
            'oshxona': [(255, 255, 0), (255, 255, 224), (255, 250, 205)],
            'eco': [(34, 139, 34), (144, 238, 144), (152, 251, 152)],
            'tungi': [(25, 25, 112), (70, 130, 180), (100, 149, 237)],
            'lux': [(128, 0, 128), (147, 112, 219), (186, 85, 211)],
            'ofis': [(105, 105, 105), (119, 136, 153), (176, 196, 222)],
            'royal': [(255, 215, 0), (255, 140, 0), (255, 165, 0)],
        }
        
        curtains = Curtain.objects.all()
        
        for curtain in curtains:
            # Eski rasmlarni o'chirish
            CurtainImage.objects.filter(curtain=curtain).delete()
            
            self.stdout.write(f'  {curtain.title} uchun rasmlar yaratilmoqda...')
            
            curtain_type = self.get_curtain_type(curtain.title.lower())
            colors = color_schemes.get(curtain_type, color_schemes['klassik'])
            
            # 3 ta rasm yaratish
            for i in range(3):
                image = self.create_curtain_image(colors, i)
                
                # Rasm faylini saqlash
                image_name = f'{curtain.slug}_{i+1}.jpg'
                
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                image_content = ContentFile(output.getvalue(), image_name)
                
                # CurtainImage yaratish
                curtain_image = CurtainImage.objects.create(
                    curtain=curtain,
                    order=i,
                    alt_text=f'{curtain.title} - Rasm {i+1}',
                    is_main=(i == 0)
                )
                
                curtain_image.image.save(image_name, image_content, save=True)
                self.stdout.write(f'    + {image_name} yaratildi')
        
        self.stdout.write(self.style.SUCCESS('Barcha parda rasmlari yaratildi!'))
    
    def get_curtain_type(self, title):
        """Parda nomiga qarab turini aniqlash"""
        if 'klassik' in title:
            return 'klassik'
        elif 'zamonaviy' in title or 'oq' in title:
            return 'zamonaviy' 
        elif 'hashamatli' in title or 'bej' in title:
            return 'hashamatli'
        elif 'bolalar' in title or 'pushti' in title:
            return 'bolalar'
        elif 'oshxona' in title or 'sariq' in title:
            return 'oshxona'
        elif 'eco' in title or 'yashil' in title:
            return 'eco'
        elif 'tungi' in title or 'kok' in title:
            return 'tungi'
        elif 'lux' in title or 'binafsha' in title:
            return 'lux'
        elif 'ofis' in title or 'kulrang' in title:
            return 'ofis'
        elif 'royal' in title or 'oltin' in title:
            return 'royal'
        else:
            return 'klassik'
    
    def create_curtain_image(self, colors, index):
        """Parda rasmi yaratish"""
        width, height = 800, 600
        base_color = colors[index % len(colors)]
        
        # Rasm yaratish
        image = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(image)
        
        # Parda naqshini qo'shish
        self.add_pattern(draw, width, height, colors, index)
        
        # Tekstura qo'shish
        self.add_texture(draw, width, height, base_color)
        
        return image
    
    def add_pattern(self, draw, width, height, colors, pattern_type):
        """Naqsh qo'shish"""
        secondary_color = colors[(pattern_type + 1) % len(colors)]
        
        if pattern_type == 0:  # Vertikal chiziqlar
            for x in range(0, width, 80):
                draw.rectangle([x, 0, x+8, height], fill=secondary_color)
        elif pattern_type == 1:  # Gorizontal chiziqlar
            for y in range(0, height, 100):
                draw.rectangle([0, y, width, y+12], fill=secondary_color)
        else:  # Diagonal
            for i in range(-height, width, 40):
                draw.line([(i, 0), (i+height, height)], fill=secondary_color, width=3)
    
    def add_texture(self, draw, width, height, base_color):
        """To'qima teksturasi"""
        lighter = tuple(min(255, c + 20) for c in base_color)
        darker = tuple(max(0, c - 20) for c in base_color)
        
        # Vertikal tekstura
        for x in range(0, width, 3):
            color = lighter if x % 6 == 0 else darker
            draw.line([(x, 0), (x, height)], fill=color, width=1)