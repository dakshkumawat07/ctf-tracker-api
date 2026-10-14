# 🚩 CTF Tracker API

A REST API for tracking CTF (Capture The Flag) competitions: the events you play, the challenges inside them, and your writeups for each challenge. Built with Django REST Framework, JWT authentication and PostgreSQL, with every user's data kept private to them.

## 🌐 Live Deployment
- **API base URL:** https://ctf-tracker-api.onrender.com/api/
- **Health check:** https://ctf-tracker-api.onrender.com/
- **Frontend consuming this API:** [ctf-tracker-frontend](https://github.com/dakshkumawat07/ctf-tracker-frontend), live at https://ctf-tracker-frontend.vercel.app

> ⚠️ Hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after idle can take 30–60 seconds while the service wakes up.

## 📖 Project Overview
Anyone who plays CTFs ends up with scattered notes: which event, which challenge, what points, how it was solved. This API gives that a structure. A user registers, logs in, and manages three linked resources: **events**, the **challenges** inside each event, and **writeups** for each challenge. Built as the backend of a full-stack mini project (frontend and backend deployed separately and wired together).

## ✨ Features
- User registration and JWT login (access + refresh tokens)
- Three related resources with **full CRUD on all of them**: Event → Challenge → Writeup
- **Per-user data isolation:** every query is scoped through the owner chain, so you only ever see your own data
- **Ownership validation on writes:** you cannot attach a challenge to someone else's event, or a writeup to someone else's challenge
- Query filters: challenges by `event` and `solved`, writeups by `challenge`
- Input validation with clear, field-level error messages
- Correct HTTP status codes (200 / 201 / 204 / 400 / 401 / 404)
- CORS restricted to an explicit list of frontend origins
- Environment-based configuration: no secrets in source control
- Production setup: Gunicorn, WhiteNoise and a hosted PostgreSQL database

## 🛠 Tech Stack
| Layer | Technology |
|---|---|
| Language | Python 3 |
| Framework | Django 6.1 + Django REST Framework |
| Authentication | djangorestframework-simplejwt (JWT) |
| Database | PostgreSQL on Neon (production) / SQLite (local) |
| App server | Gunicorn |
| Static files | WhiteNoise |
| Hosting | Render (API) |
| Configuration | python-decouple + dj-database-url |
| CORS | django-cors-headers |

## 🗂 Data Model
```
User ──< Event ──< Challenge ──< Writeup
```

| Model | Fields |
|---|---|
| **Event** | `name`, `platform`, `event_date` (optional), `url` (optional), `created_at`, `owner` |
| **Challenge** | `event`, `title`, `category` (web / crypto / pwn / reverse / forensics / misc), `points`, `solved`, `created_at` |
| **Writeup** | `challenge`, `title`, `content`, `tools_used` (optional), `created_at` |

Deleting an event deletes its challenges, and deleting a challenge deletes its writeups (cascade).

## 📡 API Endpoints
All endpoints except health check, register and login require the header
`Authorization: Bearer <access_token>`.

### Auth and health
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | No | Health check, returns `{"status": "ok", ...}` |
| POST | `/api/auth/register/` | No | Create an account. Body: `{"username", "password", "email"}` (password min 6 characters, email optional) |
| POST | `/api/auth/login/` | No | Log in. Body: `{"username", "password"}`. Returns `access` and `refresh` tokens |
| POST | `/api/auth/refresh/` | No | Get a new access token. Body: `{"refresh"}` |

### Events
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/events/` | List your events |
| POST | `/api/events/` | Create an event. Body: `{"name", "platform", "event_date", "url"}` (only `name` is required) |
| GET | `/api/events/{id}/` | Retrieve one event |
| PUT / PATCH | `/api/events/{id}/` | Update an event (PUT needs all fields, PATCH accepts a subset) |
| DELETE | `/api/events/{id}/` | Delete an event and its challenges |

### Challenges
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/challenges/` | List your challenges. Filters: `?event=<id>`, `?solved=true\|false` |
| POST | `/api/challenges/` | Create a challenge. Body: `{"event", "title", "category", "points"}` |
| GET | `/api/challenges/{id}/` | Retrieve one challenge |
| PUT / PATCH | `/api/challenges/{id}/` | Update a challenge (including `solved`) |
| DELETE | `/api/challenges/{id}/` | Delete a challenge and its writeups |

### Writeups
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/writeups/` | List your writeups. Filter: `?challenge=<id>` |
| POST | `/api/writeups/` | Create a writeup. Body: `{"challenge", "title", "content", "tools_used"}` |
| GET | `/api/writeups/{id}/` | Retrieve one writeup |
| PUT / PATCH | `/api/writeups/{id}/` | Update a writeup |
| DELETE | `/api/writeups/{id}/` | Delete a writeup |

### Example requests
**Log in**
```bash
curl -X POST https://ctf-tracker-api.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"yourpassword"}'
```
Response `200`:
```json
{ "refresh": "<refresh_token>", "access": "<access_token>" }
```

**Create an event**
```bash
curl -X POST https://ctf-tracker-api.onrender.com/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name":"PicoCTF 2026","platform":"picoCTF"}'
```
Response `201`:
```json
{
  "id": 1,
  "name": "PicoCTF 2026",
  "platform": "picoCTF",
  "event_date": null,
  "url": "",
  "created_at": "2026-10-13T11:25:58.529069Z"
}
```

**Create a challenge**
```bash
curl -X POST https://ctf-tracker-api.onrender.com/api/challenges/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"event":1,"title":"Cookie Monster","category":"web","points":100}'
```
Response `201`:
```json
{
  "id": 1,
  "event": 1,
  "event_name": "PicoCTF 2026",
  "title": "Cookie Monster",
  "category": "web",
  "points": 100,
  "solved": false,
  "created_at": "2026-10-13T11:25:58.579226Z"
}
```

### Error responses
| Situation | Status | Body |
|---|---|---|
| No token | `401` | `{"detail": "Authentication credentials were not provided."}` |
| Blank required field | `400` | `{"name": ["This field may not be blank."]}` |
| Adding a challenge to someone else's event | `400` | `{"event": ["You can only add challenges to your own events."]}` |
| Resource not found, or owned by another user | `404` | `{"detail": "No Event matches the given query."}` |

## ⚙️ Local Setup
```bash
git clone https://github.com/dakshkumawat07/ctf-tracker-api.git
cd ctf-tracker-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```env
SECRET_KEY=django-insecure-local-dev-key-change-in-prod
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Apply migrations and run the server:
```bash
python manage.py migrate
python manage.py runserver
```
The API is now available at `http://127.0.0.1:8000/api/`. To use it with the React frontend, run the frontend on port `5173` (see [ctf-tracker-frontend](https://github.com/dakshkumawat07/ctf-tracker-frontend)).

## 🔐 Environment Variables
| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django cryptographic signing key (required) | a long random string |
| `DEBUG` | Debug mode, **must be `False` in production** | `False` |
| `ALLOWED_HOSTS` | Hostnames Django will serve, comma separated | `.onrender.com` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host/db` |
| `CORS_ALLOWED_ORIGINS` | Frontend origins allowed to call the API, comma separated, no trailing slash | `https://ctf-tracker-frontend.vercel.app` |

## 🚢 Deployment
- **API:** Render Web Service
  - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
  - Start command: `gunicorn core.wsgi --bind 0.0.0.0:$PORT`
- **Database:** PostgreSQL hosted on Neon. Render's free tier allows only one free Postgres database per workspace, so the connection string is supplied through `DATABASE_URL` instead.
- **Secrets:** all set in the hosting dashboard, never committed to git.
- **Migrations:** run in the build step, because Render's free tier has no release-command or shell access.
- **CORS:** the deployed frontend's exact origin is listed in `CORS_ALLOWED_ORIGINS`.

## 📁 Project Structure
```
ctf-tracker-api/
├── core/
│   ├── settings.py      # environment-driven configuration
│   └── urls.py          # root routes: health, admin, auth, API
├── tracker/
│   ├── models.py        # Event, Challenge, Writeup
│   ├── serializers.py   # validation and ownership checks
│   ├── views.py         # owner-scoped viewsets, register view
│   ├── urls.py          # DRF router
│   └── migrations/
├── manage.py
├── requirements.txt
└── README.md
```

## 🔒 Security Design
- **Query scoping:** each viewset filters by the owner chain (`owner`, `event__owner`, `challenge__event__owner`), so other users' records return `404` and never appear in lists.
- **Write validation:** serializers reject foreign keys that point at another user's records, which prevents cross-account writes.
- **Hashed passwords:** accounts are created with `create_user`, so passwords are never stored in plain text.
- **Short-lived tokens:** access tokens last 30 minutes and refresh tokens one day.
- **Explicit CORS allow-list:** no wildcard origins.
- **No secrets in git:** `.env` is ignored, and production values live in the hosting dashboard.

## 🧠 Concepts Demonstrated
- Designing related resources and cascading relationships
- JWT authentication flow (access and refresh tokens)
- Scoping querysets and validating relations for per-user authorization
- Serializer-level validation with readable, field-level errors
- Query-parameter filtering on list endpoints
- 12-factor style configuration and a real production deployment (Gunicorn, WhiteNoise, hosted PostgreSQL)

## 🔭 Planned Improvements
- Pagination and search on list endpoints
- Tags and file attachments on writeups
- Per-event statistics endpoint (solve rate, points by category)
- Rate limiting on the auth endpoints
- Automated tests for the ownership rules

## 👤 Author
Daksh Kumawat — [@dakshkumawat07](https://github.com/dakshkumawat07)
