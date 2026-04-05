import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festms.settings')
import django
django.setup()
from django.urls import reverse
try:
    print('REVERSE IS:', reverse('bulk_delete_participants'))
except Exception as e:
    print('ERROR:', str(e))
