from django.db import models
from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField, PPOIField


class Image(models.Model):
    name = models.CharField(max_length=255)
    image = VersatileImageField(
        'Image',
        upload_to='images/',
        ppoi_field='image_ppoi'
    )
    image_ppoi = PPOIField()

    def __str__(self):
        return self.name
    
class donor(models.Model):
    d_name = models.CharField(max_length=255)
    email = models.CharField(max_length=55)
    # donations = models.OneToManyField(invent,related_name='donations')
    phone_no = models.IntegerField()
    points = models.PositiveBigIntegerField(default=0)
    locality = models.TextField(default="hj")
    city = models.CharField(max_length=200)
    longitude = models.DecimalField(decimal_places=10,max_digits=15)
    latitude = models.DecimalField(decimal_places=10,max_digits=15)

    def __str__(self):
        return self.d_name


class ngo(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=55)
    phone_no = models.IntegerField()
    rating = models.DecimalField(decimal_places=2,max_digits=4)
    locality = models.TextField(default="ghjv")
    city = models.CharField(max_length=200)
    longitude = models.DecimalField(decimal_places=10,max_digits=15)
    latitude = models.DecimalField(decimal_places=10,max_digits=15)

    def __str__(self):
        return self.name

class invent(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=10)
    # donor_id = models.ForeignKey(donor, on_delete=models.CASCADE, related_name='donor1', related_query_name='donor1')
    # category = models.ManyToManyField(Category, related_name='products')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', related_query_name='comment')
    start_date = models.DateField(auto_now_add=True)
    image = models.ManyToManyField('inventory.Image', related_name='products')
    exp_date = models.DateField()
    status = models.BooleanField(default=True)
    desc = models.TextField(default="xyz")

    def __str__(self):
        return self.name
    

class chat(models.Model):
    text = models.TextField()
    sent = models.DateField(auto_now_add=True)
    seen = models.DateField()
    sent_time = models.TimeField(auto_now_add=True)
    seen_time = models.TimeField()

    
class stats(models.Model):
    plates_served_week = models.IntegerField()
    city = models.CharField(max_length=250)
    plates_served_month = models.IntegerField()
    plates_served_total = models.IntegerField()

    def __str__(self):
        return self.city

