import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from apps.curtains.models import Curtain, CurtainImage
from PIL import Image, ImageDraw, ImageFont
import random


class Command(BaseCommand):
    help = 'Har bir parda uchun demo rasmlar yaratish'

    def handle(self, *args, **options):
        self.stdout.write('Parda rasmlarini yaratish boshlandi...')
        
        # Rang palitralari har xil parda turlari uchun
        color_schemes = {
            'klassik': [(139, 69, 19), (160, 82, 45), (205, 133, 63), (222, 184, 135)],  # Jigarrang tonlar
            'zamonaviy': [(220, 220, 220), (192, 192, 192), (169, 169, 169), (128, 128, 128)],  # Kulrang tonlar  
            'hashamatli': [(218, 165, 32), (255, 215, 0), (255, 248, 220), (250, 235, 215)],  # Oltin tonlar
            'bolalar': [(255, 182, 193), (255, 228, 225), (255, 240, 245), (255, 228, 196)],  # Pushti tonlar
            'oshxona': [(255, 255, 0), (255, 255, 224), (255, 250, 205), (255, 228, 181)],  # Sariq tonlar
            'eco': [(34, 139, 34), (144, 238, 144), (152, 251, 152), (173, 255, 47)],  # Yashil tonlar
            'tungi': [(25, 25, 112), (70, 130, 180), (100, 149, 237), (135, 206, 235)],  # Ko'k tonlar
            'lux': [(128, 0, 128), (147, 112, 219), (186, 85, 211), (221, 160, 221)],  # Binafsha tonlar
            'ofis': [(105, 105, 105), (119, 136, 153), (176, 196, 222), (230, 230, 250)],  # Kulrang-ko'k
            'royal': [(255, 215, 0), (255, 140, 0), (255, 165, 0), (255, 228, 181)],  # Oltin-sariq
        }
        
        # Parda naqshlari
        patterns = ['geometrik', 'gul', 'klassik', 'minimalist', 'vintage']
        
        curtains = Curtain.objects.all()
        
        for curtain in curtains:
            self.stdout.write(f'  {curtain.title} uchun rasmlar yaratilmoqda...')
            
            # Parda turiga qarab rang sxemasini tanlash
            curtain_type = self.get_curtain_type(curtain.title.lower())
            colors = color_schemes.get(curtain_type, color_schemes['klassik'])
            
            # Har bir parda uchun 3-4 ta rasm yaratish
            for i in range(random.randint(3, 4)):
                image = self.create_curtain_image(curtain, colors, i)
                
                # Rasm faylini saqlash
                image_name = f'{curtain.slug}_{i+1}.jpg'
                image_path = os.path.join('curtains', '2024', '09', '02', image_name)
                
                # PIL rasmini Django fayliga aylantirish
                from io import BytesIO
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                image_content = ContentFile(output.getvalue(), image_name)
                
                # CurtainImage obyektini yaratish
                curtain_image, created = CurtainImage.objects.get_or_create(
                    curtain=curtain,
                    order=i,
                    defaults={
                        'alt_text': f'{curtain.title} - Rasm {i+1}',
                        'is_main': False  # Keyinroq birinchisini asosiy qilamiz
                    }
                )
                
                if created:
                    curtain_image.image.save(image_name, image_content, save=True)
                    self.stdout.write(f'    + {image_name} yaratildi')
            
            # Birinchi rasmni asosiy qilish
            first_image = CurtainImage.objects.filter(curtain=curtain, order=0).first()
            if first_image:
                first_image.is_main = True
                first_image.save()
        
        self.stdout.write(
            self.style.SUCCESS('Barcha parda rasmlari muvaffaqiyatli yaratildi!')
        )
    
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
    
    def create_curtain_image(self, curtain, colors, index):
        """Parda rasmi yaratish"""
        # Rasm o'lchami
        width, height = 800, 600
        
        # Asosiy rang tanlash
        base_color = colors[index % len(colors)]
        
        # Rasm yaratish
        image = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(image)
        
        # Parda naqshini qo'shish
        self.add_curtain_pattern(draw, width, height, colors, index)
        
        # Parda to'qimasi effektini qo'shish
        self.add_texture_effect(draw, width, height, base_color)
        
        return image
    
    def add_curtain_pattern(self, draw, width, height, colors, pattern_type):
        """Parda naqshini qo'shish"""
        secondary_color = colors[(pattern_type + 1) % len(colors)]
        
        if pattern_type == 0:  # Vertikal chiziqlar (klassik parda)
            for x in range(0, width, 80):
                draw.rectangle([x, 0, x+10, height], fill=secondary_color)
        
        elif pattern_type == 1:  # Gorizontal chiziqlar
            for y in range(0, height, 100):
                draw.rectangle([0, y, width, y+15], fill=secondary_color)
        
        elif pattern_type == 2:  # Diagonal naqsh
            for i in range(-height, width, 50):
                draw.line([(i, 0), (i+height, height)], fill=secondary_color, width=5)
        
        elif pattern_type == 3:  # Doira naqshlari
            for x in range(100, width-100, 150):
                for y in range(100, height-100, 150):
                    draw.ellipse([x-20, y-20, x+20, y+20], outline=secondary_color, width=3)
    
    def add_texture_effect(self, draw, width, height, base_color):
        """To'qima effekti qo'shish"""
        # Yorug'lik va soya effekti
        lighter_color = tuple(min(255, c + 30) for c in base_color)
        darker_color = tuple(max(0, c - 30) for c in base_color)
        
        # Vertikal tekstura
        for x in range(0, width, 4):
            color = lighter_color if x % 8 == 0 else darker_color
            draw.line([(x, 0), (x, height)], fill=color, width=1)
        
        # Gorizontal tekstura (nozikroq)
        for y in range(0, height, 6):
            color = darker_color if y % 12 == 0 else lighter_color
            draw.line([(0, y), (width, y)], fill=color, width=1)