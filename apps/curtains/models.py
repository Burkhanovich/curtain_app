from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=225)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Curtain(models.Model):
    title=models.CharField(max_length=225)
    content = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='curtains')
    views=models.PositiveIntegerField(default=0)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




