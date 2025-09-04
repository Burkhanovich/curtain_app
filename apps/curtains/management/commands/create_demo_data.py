from django.core.management.base import BaseCommand
from apps.curtains.models import Category, Color, Curtain, CurtainImage
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Demo ma\'lumotlar yaratish'

    def handle(self, *args, **options):
        self.stdout.write('Demo ma\'lumotlar yaratilmoqda...')

        # Kategoriyalar yaratish
        categories_data = [
            'Klassik Pardalar',
            'Zamonaviy Pardalar', 
            'Hashamatli Pardalar',
            'Bolalar Xonasi Pardalari',
            'Oshxona Pardalari',
            'Yotoq Xonasi Pardalari',
            'Mehmonxona Pardalari',
            'Ofis Pardalari'
        ]
        
        categories = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(title=cat_name)
            categories.append(category)
            if created:
                self.stdout.write(f'Kategoriya yaratildi: {cat_name}')

        # Ranglar yaratish
        colors_data = [
            ('Oq', '#FFFFFF'),
            ('Qora', '#000000'),
            ('Qizil', '#DC143C'),
            ('Ko\'k', '#0000FF'),
            ('Yashil', '#228B22'),
            ('Sariq', '#FFD700'),
            ('Jigarrang', '#8B4513'),
            ('Kulrang', '#808080'),
            ('Bej', '#F5F5DC'),
            ('Qizil-jigarrang', '#A0522D'),
            ('To\'q ko\'k', '#000080'),
            ('Oltin', '#DAA520'),
            ('Kumush', '#C0C0C0'),
            ('Pushti', '#FFC0CB'),
            ('Binafsha', '#8A2BE2'),
        ]
        
        colors = []
        for color_name, hex_code in colors_data:
            color, created = Color.objects.get_or_create(
                title=color_name,
                defaults={'hex_code': hex_code}
            )
            colors.append(color)
            if created:
                self.stdout.write(f'Rang yaratildi: {color_name}')

        # Pardalar yaratish
        curtains_data = [
            {
                'title': 'Oltin Klassik Parda',
                'content': 'Yuqori sifatli ipakdan tayyorlangan klassik uslubdagi parda. Bu parda mehmon xonangizga nafis va zamonaviy ko\'rinish beradi. Maxsus texnologiya yordamida ishlab chiqilgan.',
                'price': 350000,
                'discount_price': 280000,
                'fabric_type': 'silk',
                'width': 200,
                'height': 250,
                'is_featured': True,
                'stock_quantity': 15,
            },
            {
                'title': 'Zamonaviy Oq Parda',
                'content': 'Minimalist dizayn va yumshoq to\'qimadan tayyorlangan zamonaviy parda. Har qanday interyerga mos keladi.',
                'price': 280000,
                'fabric_type': 'cotton',
                'width': 150,
                'height': 200,
                'is_featured': True,
                'stock_quantity': 22,
            },
            {
                'title': 'Hashamatli Bej Parda',
                'content': 'Premium to\'qima va nozik tikuv bilan tayyorlangan hashamatli parda. VIP xonalar uchun ideal tanlov.',
                'price': 520000,
                'discount_price': 450000,
                'fabric_type': 'velvet',
                'width': 250,
                'height': 300,
                'is_featured': True,
                'stock_quantity': 8,
            },
            {
                'title': 'Rangli Dizayn Parda',
                'content': 'Yorqin ranglar va zamonaviy naqshlar bilan bezatilgan parda. Bolalar xonasi uchun mukammal.',
                'price': 420000,
                'fabric_type': 'polyester',
                'width': 180,
                'height': 220,
                'stock_quantity': 18,
            },
            {
                'title': 'Klassik Qizil Parda',
                'content': 'An\'anaviy qizil rangdagi klassik parda. Rasmiy xonalar va katta zallarga mos.',
                'price': 390000,
                'fabric_type': 'cotton',
                'width': 220,
                'height': 280,
                'is_featured': True,
                'stock_quantity': 12,
            },
            {
                'title': 'Royal Oltin Parda',
                'content': 'Eng premium materiallar va qo\'l tikuvi bilan tayyorlangan hashamatli parda. Shohona interyerlar uchun.',
                'price': 680000,
                'discount_price': 580000,
                'fabric_type': 'silk',
                'width': 300,
                'height': 350,
                'stock_quantity': 5,
            },
            {
                'title': 'Tungi Ko\'k Parda',
                'content': 'Yotoq xonasi uchun maxsus ishlab chiqilgan qorong\'u ko\'k parda. Yorug\'likni mukammal to\'sib turadi.',
                'price': 320000,
                'fabric_type': 'linen',
                'width': 160,
                'height': 200,
                'stock_quantity': 25,
            },
            {
                'title': 'Eco Yashil Parda',
                'content': 'Ekologik toza materiallardan tayyorlangan yashil parda. Tabiiy va xavfsiz.',
                'price': 380000,
                'fabric_type': 'cotton',
                'width': 170,
                'height': 230,
                'stock_quantity': 16,
            },
            {
                'title': 'Ofis Kulrang Parda',
                'content': 'Professional muhit uchun mo\'ljallangan oddiy va zamonaviy parda. Ofislar va ishxonalar uchun.',
                'price': 250000,
                'fabric_type': 'polyester',
                'width': 150,
                'height': 180,
                'stock_quantity': 30,
            },
            {
                'title': 'Oshxona Sariq Parda',
                'content': 'Oshxona uchun maxsus ishlab chiqilgan qisqa parda. Yorqin sariq rang va oson parvarish.',
                'price': 180000,
                'fabric_type': 'cotton',
                'width': 120,
                'height': 150,
                'stock_quantity': 35,
            },
            {
                'title': 'Bolalar Pushti Parda',
                'content': 'Bolalar xonasi uchun mo\'ljallangan pushti rangdagi yoqimli parda. Xavfsiz materiallardan.',
                'price': 220000,
                'fabric_type': 'cotton',
                'width': 140,
                'height': 180,
                'stock_quantity': 20,
            },
            {
                'title': 'Lux Binafsha Parda',
                'content': 'Noyob binafsha rangdagi hashamatli parda. Maxsus tadbirlar va VIP xonalar uchun.',
                'price': 450000,
                'discount_price': 380000,
                'fabric_type': 'velvet',
                'width': 200,
                'height': 260,
                'stock_quantity': 10,
            },
        ]

        for curtain_data in curtains_data:
            # Slug yaratish
            curtain_data['slug'] = slugify(curtain_data['title'])
            
            # Tasodifiy kategoriya tanlash
            curtain_data['category'] = random.choice(categories)
            
            # Tasodifiy ko'rishlar soni
            curtain_data['views'] = random.randint(10, 500)
            
            curtain, created = Curtain.objects.get_or_create(
                title=curtain_data['title'],
                defaults=curtain_data
            )
            
            if created:
                # Tasodifiy ranglar qo'shish
                random_colors = random.sample(colors, random.randint(1, 4))
                curtain.colors.set(random_colors)
                
                self.stdout.write(f'Parda yaratildi: {curtain_data["title"]}')

        self.stdout.write(
            self.style.SUCCESS('Demo ma\'lumotlar muvaffaqiyatli yaratildi!')
        )