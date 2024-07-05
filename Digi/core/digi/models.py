
import jwt
import time
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, superuser=False, staff=True):
        if any(value is None for value in (username, email, password)):
            raise TypeError('Superusers must have a username, email and password.')

        user = self.create_user(username, email, password)
        user.is_superuser = superuser
        user.is_staff = staff
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email    

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_roles(self):
        roles  = {"staff": self.is_staff, "superuser": self.is_superuser} 
        return [x for x in  roles if roles[x]] or ['user']

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        token = jwt.encode({
            'id': self.pk,
            'sub': int(f"{self.created_at.timestamp():.0f}"),
            'exp': int(time.mktime((datetime.now() + timedelta(hours=24)).timetuple())),
            'username': self.username,
            'email': self.email,
            'company': self.company.id if self.company else None,
            'roles': self.get_roles(),
        }, settings.SECRET_KEY, algorithm='HS256')
        return token


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    colaborator_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    company_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    colaborator = models.ForeignKey('User', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)    
    created_at = models.DateTimeField(auto_now_add=True) # change to created_at
    updated_at = models.DateTimeField(auto_now=True)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    colaborator = models.ForeignKey('User', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    periodo = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True) # change to created_at



# from django.db.models import Q
# from datetime import datetime, timedelta
# fecha_actual = datetime.now()
# semana_actual = fecha_actual.isocalendar().week
# inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
# fin_semana = inicio_semana + timedelta(days=6)

# tickets_semana_actual = Ticket.objects.filter(
#     Q(fecha_creacion__gte=inicio_semana) & Q(fecha_creacion__lte=fin_semana)
# )


