Repository: xrwvm-fullstack_developer_capstone

# Cars Dealership — Full-Stack Capstone

A full-stack dealership locator and review platform for the Coursera capstone. Customers can browse dealership branches, filter by state, view details, and read or submit reviews with sentiment labels.

## Tech stack
- Django / Python for authentication and the web API
- React and Bootstrap for the interactive frontend
- Node.js / Express and MongoDB for dealership, inventory, and review data
- Flask / NLTK VADER for review sentiment analysis
- Docker Compose for MongoDB, Node API, and sentiment service
- GitHub Actions for CI checks

## Repository layout
- `server/djangoapp` — Django endpoints, models, and service clients
- `server/djangoproj` — Django configuration
- `server/frontend` — React source and static informational pages
- `server/database` — Express API, MongoDB models, and seed JSON
- `evidence/README.md` — checklist for the 28 graded evidence items
- `DEPLOYMENT.md` — deployment checklist

## Run locally on Windows

### 1. Start MongoDB, dealership API, and sentiment service
Open PowerShell:

```powershell
cd server/database
docker compose up --build -d
docker compose ps
```

This exposes MongoDB on port 27017, the dealership API on port 3030, and sentiment analysis on port 5050. The services seed their sample data when the database is empty.

### 2. Start Django
Open a second PowerShell window:

```powershell
cd server
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "from djangoapp.populate import initiate; print(initiate())"
python manage.py runserver 8000
```

If PowerShell blocks virtual-environment activation, use `.venv\Scripts\python.exe` directly for the Python commands. The local service URLs are in `server/djangoapp/.env`; they are non-secret development defaults.

### 3. Start React
Open a third PowerShell window:

```powershell
cd server/frontend
npm ci
npm start
```

React runs at `http://127.0.0.1:3000` and proxies `/djangoapp` API calls to Django at `http://127.0.0.1:8000`. Open the homepage and test registration, login, state filtering, dealer details, and posting a review.

## Useful local checks
- Django: `python manage.py check`
- Node API syntax: `cd server/database; npm test`
- React production build: `cd server/frontend; npm run build`
- API health: open `http://127.0.0.1:3030/`
- Sentiment health: open `http://127.0.0.1:5050/`

## Capstone evidence
See [the 28-task checklist](evidence/README.md). Evidence files must contain genuine results from your own run. Do not fabricate screenshots, terminal output, a passing CI run, or a deployment URL.

## Deployment status
This repository contains deployment guidance but is **not yet a live deployment**. You still need to deploy the services to your own cloud account, configure production environment variables and service URLs, verify the deployed site, and capture the requested screenshots. See [DEPLOYMENT.md](DEPLOYMENT.md).

See [LICENSE](LICENSE).
