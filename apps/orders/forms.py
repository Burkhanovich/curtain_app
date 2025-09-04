from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    """Buyurtma berish formasi"""
    
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To\'liq ismingizni kiriting'
        }),
        label='To\'liq ism'
    )
    
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 90 123 45 67'
        }),
        label='Telefon raqam'
    )
    
    customer_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'To\'liq manzilingizni kiriting (viloyat, shahar, ko\'cha, uy raqami)'
        }),
        label='To\'liq manzil'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Maxsus o\'lcham, rang yoki boshqa talablar haqida yozing (ixtiyoriy)'
        }),
        label='Qo\'shimcha ma\'lumot'
    )
    
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_address', 'notes']
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        
        # Telefon raqamni tozalash
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        # Uzbekiston telefon raqami formatini tekshirish
        if not cleaned_phone.startswith('998'):
            if len(cleaned_phone) == 9:  # 90 123 45 67
                cleaned_phone = '998' + cleaned_phone
            else:
                raise forms.ValidationError('Telefon raqam noto\'g\'ri formatda. Masalan: +998 90 123 45 67')
        
        if len(cleaned_phone) != 12:
            raise forms.ValidationError('Telefon raqam to\'liq emas. 12 raqamdan iborat bo\'lishi kerak.')
        
        # Formatlangan ko'rinishda qaytarish
        return f"+{cleaned_phone[:3]} {cleaned_phone[3:5]} {cleaned_phone[5:8]} {cleaned_phone[8:10]} {cleaned_phone[10:12]}"


class QuickOrderForm(forms.Form):
    """Tez buyurtma berish formasi - bitta mahsulot uchun"""
    
    curtain_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10'
        }),
        label='Miqdori'
    )
    
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To\'liq ismingizni kiriting'
        }),
        label='To\'liq ism'
    )
    
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 90 123 45 67'
        }),
        label='Telefon raqam'
    )
    
    customer_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'To\'liq manzilingizni kiriting'
        }),
        label='To\'liq manzil'
    )
    
    # Maxsus o'lchamlar
    custom_width = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'sm'
        }),
        label='Maxsus eni (ixtiyoriy)'
    )
    
    custom_height = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'sm'
        }),
        label='Maxsus balandligi (ixtiyoriy)'
    )
    
    custom_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Maxsus talablar yoki izohlar'
        }),
        label='Maxsus talablar'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Qo\'shimcha ma\'lumot (ixtiyoriy)'
        }),
        label='Qo\'shimcha ma\'lumot'
    )
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        
        # Telefon raqamni tozalash
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        # Uzbekiston telefon raqami formatini tekshirish
        if not cleaned_phone.startswith('998'):
            if len(cleaned_phone) == 9:  # 90 123 45 67
                cleaned_phone = '998' + cleaned_phone
            else:
                raise forms.ValidationError('Telefon raqam noto\'g\'ri formatda. Masalan: +998 90 123 45 67')
        
        if len(cleaned_phone) != 12:
            raise forms.ValidationError('Telefon raqam to\'liq emas. 12 raqamdan iborat bo\'lishi kerak.')
        
        # Formatlangan ko'rinishda qaytarish
        return f"+{cleaned_phone[:3]} {cleaned_phone[3:5]} {cleaned_phone[5:8]} {cleaned_phone[8:10]} {cleaned_phone[10:12]}"


class OrderStatusUpdateForm(forms.ModelForm):
    """Buyurtma holati o'zgartirish formasi (admin uchun)"""
    
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Holat o\'zgartirish sababi yoki izoh'
        }),
        label='Izoh'
    )
    
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class OrderSearchForm(forms.Form):
    """Buyurtma qidirish formasi"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buyurtma raqami, mijoz ismi yoki telefon raqam'
        }),
        label='Qidirish'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Barcha holatlar')] + Order.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Holati'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Sanadan'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Sanagacha'
    )