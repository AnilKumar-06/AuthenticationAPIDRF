from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            tc = tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,tc, password=None):
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email',
                              max_length=200, unique=True)
    name = models.CharField(max_length=100)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission"
        return self.is_admin
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the 'app_label"
        return True
    
    @property
    def is_staff(self):
        "is the user a member of staff"
        return self.is_admin