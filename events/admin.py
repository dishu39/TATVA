from django.contrib import admin
from .models import Event, Participant


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'date', 'venue', 'registration_count', 'max_participants']
    list_filter = ['category', 'date']
    search_fields = ['name', 'venue']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['reg_id', 'name', 'email', 'college', 'status', 'checkin_time', 'registered_at']
    list_filter = ['status', 'year', 'events']
    search_fields = ['reg_id', 'name', 'email', 'college', 'phone']
    filter_horizontal = ['events']
    readonly_fields = ['reg_id', 'qr_token', 'registered_at', 'checkin_time']
    ordering = ['-registered_at']
