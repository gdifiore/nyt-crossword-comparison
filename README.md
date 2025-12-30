# NYT Mini Crossword Comparison

Compare your NYT Mini Crossword times with others. See how you stack up against everyone else who solved the puzzle that day.

## Tech

React frontend, Flask backend, PostgreSQL database. Hosted on Heroku with daily resets.

## Running

See [docs/running.md](./docs/running.md)

## Development

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app

# Frontend
cd client
npm install
npm start
```

## Testing

```bash
pytest                # backend
cd client && npm test # frontend
```

## License

MIT
