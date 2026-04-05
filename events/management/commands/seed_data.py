from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, Participant
from django.utils import timezone
import random


EVENTS = [
    ('Hackathon', 'Technical', '2025-03-15', 'CS Lab Complex', 200),
    ('Battle of Bands', 'Cultural', '2025-03-16', 'Open Air Stage', 150),
    ('Robo Wars', 'Technical', '2025-03-15', 'Sports Ground', 80),
    ('Street Play', 'Cultural', '2025-03-17', 'Amphitheatre', 120),
    ('Coding Sprint', 'Technical', '2025-03-16', 'CS Block 101', 100),
    ('Cricket', 'Sports', '2025-03-17', 'Main Ground', 200),
    ('Quiz Bowl', 'Literary', '2025-03-16', 'Seminar Hall A', 60),
    ('Photography Walk', 'Workshop', '2025-03-15', 'Campus', 40),
]

PARTICIPANTS = [
    ('Arjun Mehta', 'arjun@iitb.ac.in', '9876543210', 'IIT Bombay', '2nd Year', 'Computer Science'),
    ('Priya Nair', 'priya@nitk.edu.in', '9876543211', 'NIT Karnataka', '3rd Year', 'Electronics'),
    ('Rahul Gupta', 'rahul@bits.ac.in', '9876543212', 'BITS Pilani', '4th Year', 'Mechanical'),
    ('Sneha Roy', 'sneha@dtu.ac.in', '9876543213', 'DTU Delhi', '2nd Year', 'Information Technology'),
    ('Karan Singh', 'karan@vit.ac.in', '9876543214', 'VIT Vellore', '1st Year', 'Computer Science'),
    ('Ananya Das', 'ananya@iitd.ac.in', '9876543215', 'IIT Delhi', '3rd Year', 'Electrical'),
    ('Mohammed Ali', 'mali@manipal.edu', '9876543216', 'Manipal University', '2nd Year', 'Civil'),
    ('Divya Rao', 'divya@nitw.ac.in', '9876543217', 'NIT Warangal', '4th Year', 'Computer Science'),
    ('Siddharth Joshi', 'sid@iitm.ac.in', '9876543218', 'IIT Madras', '3rd Year', 'Physics'),
    ('Tanvi Sharma', 'tanvi@pec.edu.in', '9876543219', 'PEC Chandigarh', '2nd Year', 'Biotechnology'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample events and participants'

    def handle(self, *args, **kwargs):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@fest.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Create events
        created_events = []
        for name, cat, date, venue, max_p in EVENTS:
            e, created = Event.objects.get_or_create(
                name=name,
                defaults={'category': cat, 'date': date, 'venue': venue, 'max_participants': max_p}
            )
            created_events.append(e)
            if created:
                self.stdout.write(f'  Event created: {name}')

        # Create participants
        for i, (name, email, phone, college, year, branch) in enumerate(PARTICIPANTS):
            if Participant.objects.filter(email=email).exists():
                continue
            p = Participant(name=name, email=email, phone=phone, college=college, year=year, branch=branch)
            p.save()
            # Assign 1-3 random events
            evts = random.sample(created_events, k=random.randint(1, 3))
            p.events.set(evts)
            # First 3 are checked-in
            if i < 3:
                p.status = 'checked-in'
                p.checkin_time = timezone.now()
                p.save()
            self.stdout.write(f'  Participant created: {name} ({p.reg_id})')

        self.stdout.write(self.style.SUCCESS('\nSeed complete!'))
        self.stdout.write('Login at /admin or / with: admin / admin123')
