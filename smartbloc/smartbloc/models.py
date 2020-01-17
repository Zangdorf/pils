from django.db import models

class User(models.Model):
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=30)

    @staticmethod
    def is_email_taken(email):
        return len(User.objects.filter(email=email)) > 0
