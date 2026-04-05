# FestMS — College Fest Management System

A Django web app to manage participants, events, and gate check-ins for a college fest.

---

## Features

- **Participant registration** with multi-event selection
- **Search & filter** participants by name, email, college, reg ID, event, or status
- **Gate check-in** via manual Reg ID entry or QR code (UUID token URL)
- **CSV export** of all participant data
- **Event management** — add/delete sub-events with category, date, venue, capacity
- **Dashboard** with live stats and event fill-rate progress bars
- **Django Admin** for full data control
- **Login-protected** — all pages require authentication

---

## Quick Start

### 1. Create virtual environment & install

```bash
cd festms
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed sample data (optional)

Creates admin user + 8 sample events + 10 participants:

```bash
python manage.py seed_data
```

Default login: **admin / admin123**

### 4. Start the server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## Pages

| URL | Description |
|---|---|
| `/` | Dashboard |
| `/register/` | Register new participant |
| `/participants/` | Search, filter, quick check-in, export |
| `/participants/<id>/` | Participant detail + QR token |
| `/participants/<id>/edit/` | Edit participant |
| `/gate/` | Gate check-in (manual entry) |
| `/gate/token/<uuid>/` | QR scan endpoint (JSON API) |
| `/events/` | Add/delete events |
| `/participants/export/` | Download CSV |
| `/admin/` | Django admin panel |

---

## QR Code Integration

Each participant has a unique `qr_token` (UUID). The gate check-in API endpoint is:

```
GET/POST  /gate/token/<qr_token>/
```

Returns JSON:
```json
{
  "status": "success",       // or "already" or "not_found"
  "reg_id": "FEST-0001",
  "name": "Arjun Mehta",
  "college": "IIT Bombay",
  "events": ["Hackathon", "Coding Sprint"],
  "checkin_time": "10:32:15"
}
```

### Generate QR codes for printing

Install `qrcode` (already in requirements), then run:

```python
import qrcode
from events.models import Participant

for p in Participant.objects.all():
    url = f"http://your-domain.com/gate/token/{p.qr_token}/"
    img = qrcode.make(url)
    img.save(f"qr_{p.reg_id}.png")
```

### Camera-based QR scanning at gate

Add [html5-qrcode](https://github.com/mebjas/html5-qrcode) to `gate.html`:

```html
<script src="https://unpkg.com/html5-qrcode"></script>
<script>
const scanner = new Html5QrcodeScanner("qr-area", { fps: 10, qrbox: 200 });
scanner.render(decodedText => {
  // decodedText is the gate token URL — fetch it
  fetch(decodedText, { method: 'POST', headers: {'X-CSRFToken': '{{ csrf_token }}'} })
    .then(r => r.json())
    .then(data => {
      // Show result to operator
      alert(`${data.status}: ${data.name}`);
    });
});
</script>
```

---

## Production Deployment

1. Set `SECRET_KEY` from environment variable
2. Set `DEBUG = False`
3. Set `ALLOWED_HOSTS` to your domain
4. Use PostgreSQL instead of SQLite (update `DATABASES` in settings)
5. Run `python manage.py collectstatic`
6. Use Gunicorn + Nginx

```bash
pip install gunicorn psycopg2-binary
gunicorn festms.wsgi:application --bind 0.0.0.0:8000
```

---

## Project Structure

```
festms/
├── festms/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── events/
│   ├── models.py          # Event, Participant
│   ├── views.py           # All views
│   ├── forms.py           # ParticipantForm, EventForm, CheckinForm
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin config
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   └── templates/
│       └── events/
│           ├── base.html
│           ├── login.html
│           ├── dashboard.html
│           ├── register.html
│           ├── participants.html
│           ├── participant_detail.html
│           ├── gate.html
│           └── events.html
├── static/
├── manage.py
└── requirements.txt
```
