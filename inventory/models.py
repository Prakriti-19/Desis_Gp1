from django.db import models
from django.contrib.auth.models import User

class donor(models.Model):
    d_name = models.CharField(max_length=255)
    email = models.CharField(max_length=55)
    phone_no = models.IntegerField()
    points = models.PositiveBigIntegerField()

    def __str__(self):
        return self.name

class inventory(models.Model):
    quantity = models.IntegerField()
    start_date = models.DateField()
    exp_date = models.DateField()
    status = models.BooleanField()
    desc = models.TextField()

    def __str__(self):
        return self.desc
    
class ngo(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=55)
    phone_no = models.IntegerField()
    rating = models.DecimalField(decimal_places=2,max_digits=5)

    def __str__(self):
        return self.name

class location(models.Model):
    locality = models.TextField()
    city = models.CharField(max_length=250)
    longitude = models.DecimalField(decimal_places=10,max_digits=15)
    latitude = models.DecimalField(decimal_places=10,max_digits=15)

    def __str__(self):
        return self.city

class chat(models.Model):
    text = models.TextField()
    sent = models.DateField()
    seen = models.DateField()
    sent_time = models.TimeField()
    seen_time = models.TimeField()

    def __str__(self):
        return self.city
    
class stats(models.Model):
    plates_served_week = models.IntegerField()
    city = models.CharField(max_length=250)
    plates_served_month = models.IntegerField()
    plates_served_total = models.IntegerField()

    def __str__(self):
        return self.city

# class Category(models.Model):
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     content = models.TextField()
#     category = models.ManyToManyField(Category, related_name='products')
#     created = models.DateField(auto_now_add=True)
#     updated = models.DateField(auto_now=True)

#     class Meta:
#         ordering = ['-created']

#     def __str__(self):
#         return self.name


# class ProductSite(models.Model):
#     name = models.CharField(max_length=255)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sites', related_query_name='site')
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sites', related_query_name='site')
#     productsize = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='sites', related_query_name='site')
#     price = models.DecimalField(max_digits=9, decimal_places=2)
#     url = models.TextField()
#     created = models.DateField(auto_now_add=True)
#     updated = models.DateField(auto_now=True)

#     def __str__(self):
#         return self.name


# class Comment(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', related_query_name='comment')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', related_query_name='comment')
#     created = models.DateField(auto_now_add=True)
#     updated = models.DateField(auto_now=True)

#     def __str__(self):
#         return self.title