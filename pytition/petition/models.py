from django.db import models


class Petition(models.Model):
    title = models.TextField()
    text = models.TextField()
    background = models.ImageField()
    top_picture = models.ImageField()
    side_text = models.TextField()


class Signature(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    confirmation_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField()
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)