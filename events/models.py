from django.db import models
import uuid


class EventCategory(models.TextChoices):
    TECHNICAL = 'Technical', 'Technical'
    CULTURAL = 'Cultural', 'Cultural'
    SPORTS = 'Sports', 'Sports'
    WORKSHOP = 'Workshop', 'Workshop'
    LITERARY = 'Literary', 'Literary'
    OTHER = 'Other', 'Other'


class YearOfStudy(models.TextChoices):
    FIRST = '1st Year', '1st Year'
    SECOND = '2nd Year', '2nd Year'
    THIRD = '3rd Year', '3rd Year'
    FOURTH = '4th Year', '4th Year'
    ALUMNI = 'Alumni / Other', 'Alumni / Other'


class Event(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=EventCategory.choices, default=EventCategory.TECHNICAL)
    date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text='Leave blank for unlimited')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'name']

    def __str__(self):
        return self.name

    @property
    def registration_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        if self.max_participants:
            return self.registration_count >= self.max_participants
        return False

    @property
    def fill_percentage(self):
        if self.max_participants and self.max_participants > 0:
            return min(100, round(self.registration_count / self.max_participants * 100))
        return 0


def generate_reg_id():
    from django.db.models import Max
    last = Participant.objects.aggregate(Max('id'))['id__max'] or 0
    return f'FEST-{(last + 1):04d}'


class Participant(models.Model):
    reg_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=300)
    year = models.CharField(max_length=20, choices=YearOfStudy.choices, blank=True)
    branch = models.CharField(max_length=150, blank=True)
    team_name = models.CharField(max_length=150, blank=True)
    events = models.ManyToManyField(Event, related_name='participants', blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('registered', 'Registered'), ('checked-in', 'Checked In')],
        default='registered'
    )
    checkin_time = models.DateTimeField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.reg_id} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.reg_id:
            # Generate reg_id after first save to get auto pk
            super().save(*args, **kwargs)
            self.reg_id = f'FEST-{self.pk:04d}'
            Participant.objects.filter(pk=self.pk).update(reg_id=self.reg_id)
        else:
            super().save(*args, **kwargs)

    @property
    def event_names(self):
        return ', '.join(self.events.values_list('name', flat=True))
