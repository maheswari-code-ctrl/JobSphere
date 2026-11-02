

# Create your models here.


from django.db import models
from django.conf import settings


class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50)
    category = models.CharField(max_length=100, default="Other")
    salary = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications"
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    applied_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Shortlisted", "Shortlisted"),
            ("Rejected", "Rejected"),
        ],
        default="Pending"
    )

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    job = models.ForeignKey(
    Job,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    saved_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.job.title}"
