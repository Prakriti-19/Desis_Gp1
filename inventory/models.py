from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Permission, Group, AbstractUser, BaseUserManager
from inventory.constants import *


class NgoManager(BaseUserManager):
    """
    NgoManager class inherits from Django's BaseUserManager class and is
    responsible for creating and managing instances of the customaised user
    model: ngo
    """

    def create_user(self, email, password=None, **kwargs):
        """
        Creates user of type ngo and sets is_ngo True

        :param self:
            reference to the instance of the class
        :param email:
            email address of the user being created.
        :param password:
            optional argument representing password for the user being created

        :return:
            instance of an ngo
        """
        if not email:
            raise ValueError(EMAIL_ERROR_MSG)

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_ngo = True
        user.save(using=self._db)
        return user


class DonorManager(BaseUserManager):
    """
    DonorManager class inherits from Django's BaseUserManager class and is
    responsible for creating and managing instances of the customaised user
    model: donor.
    """

    def create_user(self, email, password=None, **kwargs):
        """
        Creates user of type donor and sets is_ngo False

        :param self:
            reference to the instance of the class
        :param email:
            email address of the user being created.
        :param password:
            optional argument representing password for the user being created

        :return:
            instance of an donor
        """
        if not email:
            raise ValueError(EMAIL_ERROR_MSG)

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_ngo = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates a superuser of type donor

        :param self:
            reference to the instance of the class
        :param email:
            email address of the user being created.
        :param password:
            password for the user being created

        :return:
            instance of superuser
        """
        extra_fields.setdefault(STAFF_FLAG, True)
        extra_fields.setdefault(SUPERUSER_FLAG, True)
        return self.create_user(email, password, **extra_fields)


class Pincode(models.Model):
    """
    This model is used to store the information in normalized and efficient way.
    It inherits from models.Model
    """

    code = models.IntegerField()
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=MAX_LENGTH)

    def __str__(self):
        return self.city


class Ngo(AbstractUser):
    """
    ngo Class represents an ngo

    It is child class of AbstractUser Class, inheriting:
    - the fields username, password, email
    - methods for handling passwords, including password hashing and validation
    - built-in managers for creating, querying, and modifying user objects

    :return:
        instance of ngo user
    """

    ngo_name = models.CharField(max_length=MAX_LENGTH)
    email = models.EmailField(max_length=MAX_LENGTH)
    phone_no = models.CharField(max_length=SMALL_MAX_LENGTH)
    is_ngo = models.BooleanField(default=True)
    descoins = models.PositiveBigIntegerField(default=NGO_DESCOINS)
    longitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH
    )
    latitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH
    )
    pincode = models.ForeignKey(Pincode, on_delete=models.CASCADE, null=True)
    objects = NgoManager()

    def __str__(self):
        return self.ngo_name


class Donor(AbstractUser):
    """
    Represents a donor in our application and also inherits from AbstractUser Class

    :return:
        instance of donor user
    """

    donor_name = models.CharField(max_length=MAX_LENGTH)
    email = models.EmailField(max_length=MAX_LENGTH)
    phone_no = models.CharField(max_length=SMALL_MAX_LENGTH)
    descoins = models.PositiveBigIntegerField(default=DONOR_DESCOINS)
    is_ngo = models.BooleanField(default=False)
    longitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH, null=True
    )
    latitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH, null=True
    )
    pincode = models.ForeignKey(Pincode, on_delete=models.CASCADE, null=True)
    groups = models.ManyToManyField(Group, related_name=DONOR_GP)
    user_permissions = models.ManyToManyField(Permission, related_name=DONOR_PERMISSION)

    objects = DonorManager()

    def __str__(self):
        return self.donor_name

    def donations_made(self):
        """
        Returns all the donations made by that instance

        :param self:
            reference to the instance of the class i.e donor

        :return:
            QuerySet object of the donations
        """
        return Donations.objects.filter(donor_id=self.id)


class Donations(models.Model):
    """
    Represents food donation made by a donor

    :param donor_id:
        maps this donation to the donor who has made it
    :param ngo_id:
        maps this donation to the ngo who will take it
    :param donor_status:
        bool flag representing if donor has donated the donation
    :param ngo_status:
        bool flag representing if ngo has recieved the donation

    :return:
        instance of donation
    """

    TYPE_CHOICES = [
        (HOME_FOOD, "Home Food"),
        (PARTY, "Party"),
        (RESTAURANT, "Restaurant"),
        (OTHER, "Other"),
    ]
    id = models.AutoField(primary_key=True)
    donor_id = models.ForeignKey(Donor, on_delete=models.CASCADE)
    ngo_id = models.ForeignKey(
        Ngo,
        on_delete=models.CASCADE,
        related_name=NGO_DONATION,
        blank=True,
        null=True,
    )
    donation_date = models.DateField(null=True)
    exp_date = models.DateField()
    longitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH
    )
    latitude = models.DecimalField(
        decimal_places=DECIMAL_MAX_LENGTH, max_digits=SMALL_MAX_LENGTH
    )
    pincode = models.ForeignKey("pincode", on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    description = models.TextField()
    ngo_status = models.BooleanField(default=True)
    donor_status = models.BooleanField(default=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=OTHER)

    def __str__(self):
        return self.description

class Transaction_code(models.Model):
    """
    This model is used to store the information in normalized and efficient way.
    """
    code = models.IntegerField()
    sender =  models.CharField(max_length=MAX_LENGTH, default="donor")
    receiver = models.CharField(max_length=MAX_LENGTH, default="receiver")
    def __str__(self):
        return self.sender
    
class Transaction(models.Model):
    """
    Represents Transaction taking place between NGO, Donor and Our side
    """
    code = models.ForeignKey(Transaction_code, on_delete=models.CASCADE, null=True)
    sender = models.IntegerField(blank=True, null=True)
    receiver = models.IntegerField(blank=True, null=True)
    descoins_transferred = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)


