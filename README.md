# CyberGame

A simple, fast-paced arcade game built with Flask and Supabase.

## Features

- **Game**: Test your reflexes by clicking targets.
- **Leaderboard**: Compete globally for the top score.
- **Profile**: Track your personal bests.
- **Authentication**: Secure login/signup powered by Supabase Auth.
- **Cyberpunk Theme**: Custom dark mode UI.

## Setup

1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Supabase**:
    -   Create a new Supabase project.
    -   Run the SQL commands in `schema.sql` in your Supabase SQL Editor to set up tables and policies.
    -   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    -   Fill in `SUPABASE_URL` and `SUPABASE_KEY` (Anon Key) from your Supabase project settings.
    -   Set a random `FLASK_SECRET_KEY`.

4.  **Run the application**:
    ```bash
    flask run
    ```
    The app will be available at `http://localhost:5000`.

## Testing

Run the test suite with:
```bash
pytest tests/
```

## Technologies

-   **Backend**: Python, Flask
-   **Database**: Supabase (PostgreSQL) + Auth
-   **Frontend**: HTML, CSS, JavaScript (Vanilla)
