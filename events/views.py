import csv
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import Participant, Event
from .forms import ParticipantForm, EventForm, CheckinForm


@login_required
def dashboard(request):
    total = Participant.objects.count()
    checked_in = Participant.objects.filter(status='checked-in').count()
    pending = total - checked_in
    event_count = Event.objects.count()
    college_count = Participant.objects.values('college').distinct().count()
    recent = Participant.objects.prefetch_related('events').order_by('-registered_at')[:8]
    events = Event.objects.annotate(reg_count=Count('participants')).order_by('date', 'name')
    context = {
        'total': total,
        'checked_in': checked_in,
        'pending': pending,
        'event_count': event_count,
        'college_count': college_count,
        'recent': recent,
        'events': events,
    }
    return render(request, 'events/dashboard.html', context)


@login_required
def register_participant(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()
            messages.success(request, f'Registered successfully! Reg ID: {participant.reg_id}')
            return redirect('register_participant')
    else:
        form = ParticipantForm()
    return render(request, 'events/register.html', {'form': form})


@login_required
def participant_list(request):
    qs = Participant.objects.prefetch_related('events').all()
    q = request.GET.get('q', '').strip()
    event_filter = request.GET.get('event', '')
    status_filter = request.GET.get('status', '')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(email__icontains=q) |
            Q(college__icontains=q) | Q(reg_id__icontains=q) |
            Q(phone__icontains=q)
        )
    if event_filter:
        qs = qs.filter(events__id=event_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    events = Event.objects.all()
    context = {
        'participants': qs,
        'events': events,
        'q': q,
        'event_filter': event_filter,
        'status_filter': status_filter,
        'total_count': qs.count(),
    }
    return render(request, 'events/participants.html', context)


@login_required
def participant_detail(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    details = [
        ('Reg ID', participant.reg_id),
        ('Email', participant.email),
        ('Phone', participant.phone),
        ('College', participant.college),
        ('Year', participant.year),
        ('Branch', participant.branch),
        ('Team', participant.team_name),
        ('Registered', participant.registered_at.strftime('%d %b %Y, %H:%M')),
    ]
    return render(request, 'events/participant_detail.html', {'participant': participant, 'details': details})


@login_required
def edit_participant(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participant updated successfully.')
            return redirect('participant_list')
    else:
        form = ParticipantForm(instance=participant)
    return render(request, 'events/register.html', {'form': form, 'editing': True, 'participant': participant})


@login_required
def delete_participant(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        name = participant.name
        participant.delete()
        messages.success(request, f'Participant "{name}" deleted.')
    return redirect('participant_list')


@login_required
def gate_checkin(request):
    form = CheckinForm()
    result = None
    if request.method == 'POST':
        form = CheckinForm(request.POST)
        if form.is_valid():
            reg_id = form.cleaned_data['reg_id'].strip().upper()
            try:
                p = Participant.objects.prefetch_related('events').get(reg_id=reg_id)
                if p.status == 'checked-in':
                    result = {'status': 'already', 'participant': p}
                else:
                    p.status = 'checked-in'
                    p.checkin_time = timezone.now()
                    p.save()
                    result = {'status': 'success', 'participant': p}
            except Participant.DoesNotExist:
                result = {'status': 'not_found', 'reg_id': reg_id}
        form = CheckinForm()

    recent_checkins = Participant.objects.filter(
        status='checked-in', checkin_time__date=timezone.now().date()
    ).order_by('-checkin_time')[:20]

    return render(request, 'events/gate.html', {
        'form': form,
        'result': result,
        'recent_checkins': recent_checkins,
        'today_count': recent_checkins.count(),
    })


@login_required
def checkin_by_token(request, token):
    """QR code endpoint — token is participant's qr_token UUID"""
    try:
        p = Participant.objects.prefetch_related('events').get(qr_token=token)
        if p.status == 'checked-in':
            status = 'already'
        else:
            p.status = 'checked-in'
            p.checkin_time = timezone.now()
            p.save()
            status = 'success'
        return JsonResponse({
            'status': status,
            'reg_id': p.reg_id,
            'name': p.name,
            'college': p.college,
            'events': list(p.events.values_list('name', flat=True)),
            'checkin_time': p.checkin_time.strftime('%H:%M:%S') if p.checkin_time else None,
        })
    except Participant.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)


@login_required
def quick_checkin(request, pk):
    """AJAX quick check-in from participant list"""
    if request.method == 'POST':
        p = get_object_or_404(Participant, pk=pk)
        if p.status != 'checked-in':
            p.status = 'checked-in'
            p.checkin_time = timezone.now()
            p.save()
        return JsonResponse({'status': 'ok', 'checkin_time': p.checkin_time.strftime('%H:%M') if p.checkin_time else ''})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def export_csv(request):
    qs = Participant.objects.prefetch_related('events').all()
    event_filter = request.GET.get('event', '')
    status_filter = request.GET.get('status', '')
    if event_filter:
        qs = qs.filter(events__id=event_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fest_participants.csv"'
    writer = csv.writer(response)
    writer.writerow(['Reg ID', 'Name', 'Email', 'Phone', 'College', 'Year', 'Branch', 'Team', 'Events', 'Status', 'Check-in Time', 'Registered At'])
    for p in qs:
        writer.writerow([
            p.reg_id, p.name, p.email, p.phone, p.college,
            p.year, p.branch, p.team_name,
            p.event_names,
            p.get_status_display(),
            p.checkin_time.strftime('%Y-%m-%d %H:%M:%S') if p.checkin_time else '',
            p.registered_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return response


@login_required
def event_list(request):
    events = Event.objects.annotate(reg_count=Count('participants')).order_by('date', 'name')
    form = EventForm()
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{form.cleaned_data["name"]}" added.')
            return redirect('event_list')
    return render(request, 'events/events.html', {'events': events, 'form': form})


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        name = event.name
        event.delete()
        messages.success(request, f'Event "{name}" deleted.')
    return redirect('event_list')

@login_required
def bulk_delete_participants(request):
    if request.method == 'POST':
        # Handles a comma-separated string if sent via AJAX or standard form array
        raw_ids = request.POST.get('participant_ids', '')
        if raw_ids:
            participant_ids = raw_ids.split(',')
            count, _ = Participant.objects.filter(pk__in=participant_ids).delete()
            messages.success(request, f'Successfully deleted {count} participant(s).')
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'error': 'No IDs provided'}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)

@login_required
def import_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        if not (excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.csv')):
            messages.error(request, 'Please upload a valid .xlsx or .csv file.')
            return redirect('dashboard')
            
        try:
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                df = pd.read_excel(excel_file)
                
            cols = [str(c).lower() for c in df.columns]
            
            def get_col(substr, default=None):
                for c in cols:
                    if substr in c:
                        return c
                return default

            name_col = get_col('name')
            email_col = get_col('mail')
            phone_col = get_col('phone') or get_col('contact')
            college_col = get_col('college') or get_col('university') or get_col('institution')
            year_col = get_col('year')
            branch_col = get_col('branch') or get_col('course')
            team_col = get_col('team')
            events_col = get_col('event')
            
            if not name_col or not email_col:
                messages.error(request, 'Could not find required columns (Name, Email) in the file.')
                return redirect('dashboard')

            all_events = {e.name.lower().strip(): e for e in Event.objects.all()}
            count_new = 0
            count_updated = 0
            
            for index, row in df.iterrows():
                email = str(row.get(df.columns[cols.index(email_col)], '')).strip()
                if not email or email.lower() == 'nan':
                    continue
                    
                name = str(row.get(df.columns[cols.index(name_col)], '')).strip()
                phone = str(row.get(df.columns[cols.index(phone_col)], '')) if phone_col else ''
                college = str(row.get(df.columns[cols.index(college_col)], '')) if college_col else ''
                year = str(row.get(df.columns[cols.index(year_col)], '')) if year_col else ''
                branch = str(row.get(df.columns[cols.index(branch_col)], '')) if branch_col else ''
                team = str(row.get(df.columns[cols.index(team_col)], '')) if team_col else ''
                
                if phone.lower() == 'nan': phone = ''
                if college.lower() == 'nan': college = ''
                if year.lower() == 'nan': year = ''
                if branch.lower() == 'nan': branch = ''
                if team.lower() == 'nan': team = ''
                
                participant, created = Participant.objects.update_or_create(
                    email=email,
                    defaults={
                        'name': name,
                        'phone': phone,
                        'college': college,
                        'year': year,
                        'branch': branch,
                        'team_name': team
                    }
                )
                
                if created:
                    count_new += 1
                else:
                    count_updated += 1
                
                if events_col:
                    events_val = str(row.get(df.columns[cols.index(events_col)], ''))
                    if events_val and events_val.lower() != 'nan':
                        event_names_raw = [e.strip() for e in events_val.split(',')]
                        matched_events = []
                        for raw_en in event_names_raw:
                            if not raw_en: continue
                            en = raw_en.lower()
                            
                            found = False
                            for key in all_events:
                                if key in en or en in key:
                                    matched_events.append(all_events[key])
                                    found = True
                                    break
                                    
                            if not found:
                                # Auto-create the newly detected event
                                new_event = Event.objects.create(name=raw_en, category='Other')
                                all_events[new_event.name.lower().strip()] = new_event
                                matched_events.append(new_event)
                                
                        if matched_events:
                            participant.events.add(*matched_events)
                            
            messages.success(request, f'Successfully imported data! {count_new} created, {count_updated} updated.')
            
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
            
    return redirect('dashboard')
