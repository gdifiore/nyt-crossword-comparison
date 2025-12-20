### Locally
[PostgreSQL on Linux](./postgresql.md)

#### Requirements
- Python 3.8 or higher
- Node.js 14.x (specified in package.json)
- PostgreSQL 12 or higher

#### Set up Environment
```
(in repository root dir)
python -m venv .venv
. .venv/scripts/activate

pip install -r requirements.txt
```

Sample `.env` for app config (see `.env.example` for complete reference)
```
# place in root directory with app.py
DATABASE_HOST="localhost"
DATABASE_NAME="nytcrosswordcomparison"
DATABASE_USERNAME="postgres"
DATABASE_PASSWORD="password"
```

#### Building Clientside Web App
```
(new terminal)
sudo apt install npm

cd client/
npm install
npm run build
```

#### Start Website
`python app.py`

### Heroku
Some steps may be missing.

#### Heroku App Creation
Most of [this tutorial](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true#create-and-deploy-the-app) for setup and deploying.

For creating the Postgres DB, follow [this](https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1).

For setting environment variables (from .env) use [this](https://devcenter.heroku.com/articles/config-vars).

#### Resetting DB Daily
Since the site is meant to compare mini crossword times for each day, the DB must be reset each day at midnight.

1: Install the Heroku Scheduler add-on in your app

`heroku addons:create scheduler:standard`

2: Schedule the Script

Run the Heroku Scheduler dashboard:

`heroku addons:open scheduler`

Add a new job:

- Command: `python clear_db.py`
- Frequency: Daily (midnight EST)