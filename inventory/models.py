from django.db import models
from django.contrib.auth.models import Permission,Group
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import  BaseUserManager

class NgoManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email is required')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_ngo = True
        user.is_donor = False
        user.save(using=self._db)
        return user    

class DonorManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email is required')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_donor = True
        user.is_ngo = False
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class pincode(models.Model):
    code = models.IntegerField(default=248001)
    city = models.CharField(max_length=250,default="es")
    state= models.CharField(max_length=250,default="qw")
    def __str__(self):
        return self.city

class ngo(AbstractUser):
    ngo_name = models.CharField(max_length=255,default="a")
    email = models.CharField(max_length=55,default="b")
    phone_no = models.IntegerField(default=123456789)
    is_ngo = models.BooleanField(default=True)
    is_donor = models.BooleanField(default=False)
    pincode = models.ForeignKey(pincode, on_delete=models.CASCADE,null=True)
    groups = models.ManyToManyField(Group, related_name='ngo_groups')
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='ngo_user_permissions',
    )
    objects = NgoManager()
    def __str__(self):
        return self.ngo_name
    pass
    
class donor(AbstractUser):
    donor_name = models.CharField(max_length=255)
    email = models.CharField(max_length=55)
    phone_no = models.IntegerField(default=123456789)
    points = models.PositiveBigIntegerField(default=0)
    is_ngo = models.BooleanField(default=False)
    is_donor = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='donor_groups')
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='donor_user_permissions',
    )

    objects = DonorManager()
    def __str__(self):
        return self.donor_name
    pass
    

class donations(models.Model):
    id = models.AutoField(primary_key=True)
    donor_id = models.ForeignKey(donor, on_delete=models.CASCADE)
    ngo_id = models.ForeignKey(ngo, on_delete=models.CASCADE, related_name='ngo_donations', blank=True, null=True)
    exp_date = models.DateField()
    longitude = models.DecimalField(decimal_places=10,max_digits=15)
    latitude = models.DecimalField(decimal_places=10,max_digits=15)
    pincode = models.ForeignKey("pincode", on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=10)
    desc = models.TextField(default="xyz")
    donation_date = models.DateField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Call the parent save method to save the donation object
        super(donations, self).save(*args, **kwargs)
        
        # Update the donor's points
        self.donor_id.points += self.quantity
        self.donor_id.save()
    def __str__(self):
        return self.desc
    def donations_made(self):
        # return donations made by this donor
        pass
    

class chat(models.Model):
    text = models.TextField()
    sent = models.DateField(auto_now_add=True)
    seen = models.DateField()
    sent_time = models.TimeField(auto_now_add=True)
    seen_time = models.TimeField()





