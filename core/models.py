from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='site/')
    favicon = models.ImageField(upload_to='site/', blank=True)

    phone = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.TextField()

    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)

    opening_time = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name
    

    

class HeroBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()

    image = models.ImageField(upload_to='hero/')
    button_text = models.CharField(max_length=50)
    button_url = models.CharField(max_length=255)

    sort_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    


class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    icon = models.ImageField(
        upload_to='features/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title
    


    
class Testimonial(models.Model):
    name = models.CharField(max_length=100)

    city = models.CharField(
        max_length=100,
        blank=True
    )

    image = models.ImageField(
        upload_to='testimonials/'
    )

    rating = models.PositiveSmallIntegerField(default=5)

    review = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name




class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    



class ContactMessage(models.Model):

    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()

    subject = models.CharField(max_length=200)

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question
    
        

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    html_message = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    error_message = models.TextField(blank=True, null=True)

    retry_count = models.PositiveIntegerField(default=0)

    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
