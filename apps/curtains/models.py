from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    title = models.CharField(_('Nomi'), max_length=225, help_text=_('Kategoriya nomi'))
    created_date = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kategoriya')
        verbose_name_plural = _('Kategoriyalar')
        ordering = ['-created_date']
        db_table = 'categories'

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(_('Rang nomi'), max_length=225, help_text=_('Rang nomi'))
    hex_code = models.CharField(_('Rang kodi'), max_length=7, blank=True, null=True, help_text=_('#ffffff formatida'))
    created_date = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Rang')
        verbose_name_plural = _('Ranglar')
        ordering = ['title']
        db_table = 'colors'

    def __str__(self):
        return self.title


class Curtain(models.Model):
    FABRIC_CHOICES = [
        ('cotton', _('Paxta')),
        ('silk', _('Ipak')),
        ('linen', _('Zig\'ir')),
        ('polyester', _('Polyester')),
        ('velvet', _('Baxmal')),
        ('other', _('Boshqa')),
    ]

    STATUS_CHOICES = [
        ('available', _('Mavjud')),
        ('out_of_stock', _('Tugagan')),
        ('discontinued', _('To\'xtatilgan')),
    ]

    title = models.CharField(_('Nomi'), max_length=225, help_text=_('Parda nomi'))
    slug = models.SlugField(_('Slug'), max_length=255, unique=True, blank=True)
    content = models.TextField(_('Ta\'rif'), null=True, blank=True, help_text=_('Parda haqida batafsil ma\'lumot'))
    price = models.PositiveIntegerField(_('Narxi'), help_text=_('So\'mda narx'))
    discount_price = models.PositiveIntegerField(_('Chegirmali narx'), null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                               related_name='curtains', verbose_name=_('Kategoriya'))
    colors = models.ManyToManyField(Color, verbose_name=_('Ranglar'), blank=True, 
                                  related_name='curtains')
    fabric_type = models.CharField(_('Mato turi'), max_length=20, choices=FABRIC_CHOICES, 
                                 default='other')
    width = models.PositiveIntegerField(_('Eni (sm)'), null=True, blank=True)
    height = models.PositiveIntegerField(_('Balandligi (sm)'), null=True, blank=True)
    status = models.CharField(_('Holati'), max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(_('Asosiy'), default=False, 
                                    help_text=_('Asosiy sahifada ko\'rsatish'))
    is_active = models.BooleanField(_('Faol'), default=True)
    views = models.PositiveIntegerField(_('Ko\'rishlar soni'), default=0)
    stock_quantity = models.PositiveIntegerField(_('Ombordagi soni'), default=0)
    created_date = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)
    modified_date = models.DateTimeField(_('O\'zgartirilgan sana'), auto_now=True)

    class Meta:
        verbose_name = _('Parda')
        verbose_name_plural = _('Pardalar')
        ordering = ['-created_date']
        db_table = 'curtains'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_on_sale(self):
        return self.discount_price and self.discount_price < self.price

    @property
    def final_price(self):
        return self.discount_price if self.is_on_sale else self.price

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class CurtainImage(models.Model):
    curtain = models.ForeignKey(Curtain, on_delete=models.CASCADE, related_name='images',
                              verbose_name=_('Parda'))
    image = models.ImageField(_('Rasm'), upload_to='curtains/%Y/%m/%d/')
    alt_text = models.CharField(_('Alt matni'), max_length=255, blank=True)
    is_main = models.BooleanField(_('Asosiy rasm'), default=False)
    order = models.PositiveIntegerField(_('Tartib'), default=0)
    created_date = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Parda rasmi')
        verbose_name_plural = _('Parda rasmlari')
        ordering = ['order', '-created_date']
        db_table = 'curtain_images'

    def __str__(self):
        return f"{self.curtain.title} - {self.order}"




