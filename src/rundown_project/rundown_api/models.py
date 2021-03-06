from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password = None):
        if not email:
            raise ValueError("The user must have an email address")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        email = self.normalize_email(email)
        user = self.model(email = email, name = name)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, validators=[MinLengthValidator(4)])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    password = models.CharField(max_length=255,validators=[MinLengthValidator(8)])
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email


class Rundown(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    title = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    description = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class RundownDetail(models.Model):
    rundown = models.ForeignKey(Rundown, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, validators=[MinLengthValidator(4)])
    description = models.TextField(validators=[MinLengthValidator(4)])
    order_num = models.IntegerField(default=0)
    with_date = models.DateField(null=True, blank=True, default=None)

    def __str__(self):
        return self.title

class Friend(models.Model):
    requested_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="requested_by", default=None)
    user = models.ForeignKey(UserProfile, on_delete= models.CASCADE, related_name = "user", default=None)
    friend  = models.ForeignKey(UserProfile, on_delete= models.CASCADE, related_name = "friend", default=None)
    is_blocked = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)