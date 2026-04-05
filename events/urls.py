from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_participant, name='register_participant'),
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/bulk_delete/', views.bulk_delete_participants, name='bulk_delete'),
    path('participants/<int:pk>/', views.participant_detail, name='participant_detail'),
    path('participants/<int:pk>/edit/', views.edit_participant, name='edit_participant'),
    path('participants/<int:pk>/delete/', views.delete_participant, name='delete_participant'),
    path('participants/<int:pk>/checkin/', views.quick_checkin, name='quick_checkin'),
    path('participants/export/', views.export_csv, name='export_csv'),
    path('import/', views.import_excel, name='import_excel'),
    path('gate/', views.gate_checkin, name='gate_checkin'),
    path('gate/token/<uuid:token>/', views.checkin_by_token, name='checkin_by_token'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/delete/', views.delete_event, name='delete_event'),
]
