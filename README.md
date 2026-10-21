# MLBB Player Management System

A Django application for MLBB players finding teams, team staff recruiting players, and tournament organizers managing events. The authenticated dashboard is the site's entry point: anonymous visitors are sent to login first.

## Requirements

- Python 3.14 (the version pinned by `Pipfile`)
- Pipenv

The dependency manifest is `Pipfile`; keep the generated `Pipfile.lock` committed to reproduce package resolution.

## Local setup (Windows PowerShell)

From the repository root:

```powershell
py -3.14 -m pip install pipenv
pipenv install --dev
Copy-Item .env.example .env
pipenv run python IMS_Project\manage.py check
pipenv run python IMS_Project\manage.py migrate
pipenv run python IMS_Project\manage.py runserver
```

Open `http://127.0.0.1:8000/`. The root redirects to `/accounts/login/` until the visitor signs in. New accounts choose one or more responsibilities at signup. Player accounts can create their player card and must select exactly five main heroes.

`Pipenv` loads variables from `.env` for `pipenv run`. If running Django outside Pipenv, export the same environment variables in the current shell. Do not commit `.env`; use `.env.example` as a safe variable-name template only.

## Data and migrations

The default database is `IMS_Project\db.sqlite3`. Migrations are additive and preserve existing player rows; legacy player rows remain unclaimed and are not shown as user-owned public profiles. Team staff can review available unlinked records and add them to a team roster without assigning them to another user's account. Back up a database before applying migrations to any important environment:

```powershell
Copy-Item IMS_Project\db.sqlite3 IMS_Project\db.sqlite3.backup
pipenv run python IMS_Project\manage.py migrate
```

Never delete or replace a populated database to resolve a migration problem. Diagnose migration state and back up data first.

Migration `0009` updates the hero catalog to the 133 entries on the [Mobile Legends Fandom hero list](https://mobile-legends.fandom.com/wiki/List_of_heroes), uses each hero's first recommended lane, and stores its listed portrait URL; the catalog is a migration snapshot and does not synchronize automatically. Portraits are loaded from the Fandom image CDN rather than copied into this repository; if an image is unavailable, the hero tile falls back to its initial. Administrators can search, activate, and maintain hero records through Django admin. `Hero.portrait` also supports an optional local static asset path. The current profile and team forms do not accept avatar or team-logo uploads.

Tournament management currently covers tournament records and team entry review; it does not claim to implement brackets, fixtures, match results, or standings.

## Account and community workflows

- Player profiles are linked one-to-one to their Django account. Player ID/server uniqueness remains enforced across all records.
- Main hero choices are stored as ordered player-to-hero rows. Profile forms reject anything other than five distinct active heroes; the database also prevents duplicate heroes and positions.
- The profile editor includes the authenticated MLBB nickname lookup; provider timeouts, HTTP failures, and malformed responses return explicit errors.
- Player discovery is authenticated and exposes only profiles with an owner that opted into recruitment.
- Team owners/captains manage team details, add available player profiles or unlinked legacy records to rosters, review membership requests, update member responsibilities, and remove roster entries. The overview shows recently updated profiles and makes unlinked records visible only to team staff.
- Tournament organizers can create, edit, close, complete, and delete their tournaments; eligible team owners, captains, or managers can submit team entries.
- Account settings maintain email and multi-role flags, Django's built-in password reset/change flows are enabled, and the notifications page summarizes persisted team and tournament activity.
- Logout uses a CSRF-protected POST form.

## Hero catalog, analytics, and leaderboard

- **Heroes** (`/heroes/`) searches and filters the existing active hero catalog by name and the catalog's lane field, with alphabetical or lane sorting and pagination. A hero detail page shows only the stored name, lane, and portrait. The catalog does not invent tiers, win/pick/ban rates, builds, skills, or counters.
- **Portraits** continue to use portrait URLs already stored by the existing hero-catalog migrations. They load from the external image host and are not downloaded or rehosted here. A local initial is used if a portrait fails. The current source is the Mobile Legends Fandom image CDN; verify each image's license before redistributing or relying on it in a production product.
- **Player leaderboard** (`/leaderboard/`) queries account-linked player records opted in to team discovery. The default order is the app's Warrior-to-Mythical Immortal rank progression, current stars, recorded win rate, then IGN. Win-rate order uses recorded win rate, rank, stars, then IGN. Match counts are not stored, so win rates are not match-weighted. Rank and statistics are player-entered and are not verified against game servers. Filters cover IGN, role, current rank, server, and associated team. Updates are reflected on the next request; this is not a push-based real-time feed.
- The dashboard's rank/role summaries and top-player list are computed from those same opted-in player profiles. The average win rate excludes values outside 0–100. External hero meta statistics are explicitly marked unavailable.
- MLBBHub is linked as a reference, not scraped or copied. Its public hero and leaderboard pages describe statistics as approximate, its `robots.txt` disallows `/api/`, and the terms reviewed describe a license for community-submitted builds rather than granting this application a reuse license for its catalog data or artwork. No documented, authorized global-ranking or hero-statistics feed was identified for this integration. Accordingly, global player rankings and imported hero statistics are not presented as app data.

## Tests and checks

```powershell
pipenv run python IMS_Project\manage.py check
pipenv run python IMS_Project\manage.py makemigrations --check --dry-run
pipenv run python IMS_Project\manage.py test myapp
```

The test suite exercises authentication, login-first routing, player ownership, five-hero validation and persistence, data visibility, team membership permissions, tournament registration, rank/star validation, leaderboard ranking/filters/refresh behavior, and hero catalog search and detail pages.

## Configuration and deployment

Local development defaults to `DJANGO_ENV=development` and may generate an ephemeral secret key when one is not supplied. For deployment:

1. Set `DJANGO_ENV=production`.
2. Set a long, unique `DJANGO_SECRET_KEY` using the deployment platform's secret manager.
3. Set comma-separated `DJANGO_ALLOWED_HOSTS` to the real hostnames.
4. Keep `DJANGO_DEBUG=False` (production mode forces debug off).
5. Terminate TLS at the application server or trusted proxy; `DJANGO_SECURE_SSL_REDIRECT` defaults to true outside debug mode. Configure proxy SSL headers only for a trusted proxy.
6. Use a persistent production database and a production-ready WSGI/ASGI server; SQLite is the local default, not a multi-worker production database recommendation.
7. Configure `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`, `DJANGO_EMAIL_USE_TLS`, and `DJANGO_DEFAULT_FROM_EMAIL` so password-reset messages can be delivered. The console backend is for local development.
8. Run `manage.py migrate` as a controlled deployment step and run `manage.py check --deploy` against production settings.

`SECURE_SSL_REDIRECT`, secure session/CSRF cookies, and HSTS are enabled when debug is off. Adjust SSL redirect only when TLS is correctly terminated upstream; do not disable secure cookie or HSTS protections as a substitute for fixing proxy configuration.

Static assets are stored in `myapp/static/myapp` and served by Django's development server locally. Production deployments must configure `STATIC_ROOT`, run `collectstatic`, and serve static files through a suitable web server or object storage. The project currently accepts no user-uploaded media.

## Troubleshooting

- **Missing secret in production:** set `DJANGO_SECRET_KEY`; a local generated key is intentionally not used outside development.
- **Invalid host:** add the hostname to `DJANGO_ALLOWED_HOSTS`.
- **Migration conflict:** back up the database, inspect `showmigrations myapp`, and resolve migration history without deleting data.
- **No heroes appear:** run migrations to apply the local catalog seed, then inspect the Hero records in Django admin.
- **Lookup service errors:** the nickname lookup depends on an external provider. Network outages, provider changes, and malformed provider responses are surfaced to the user; test the endpoint from the target network rather than assuming it is always available.
