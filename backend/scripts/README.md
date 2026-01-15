# Database Scripts

This directory contains utility scripts for database management.

## Available Scripts

### init_db.py

Initializes the database by running all Alembic migrations.

**Usage:**
```bash
cd backend
python scripts/init_db.py
```

**What it does:**
1. Runs all pending Alembic migrations
2. Creates all database tables
3. Inserts seed data (builtin scripts and default Agent configurations)

## Manual Migration Commands

If you prefer to use Alembic directly:

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Upgrade to latest version
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Create a new migration (auto-generate)
alembic revision --autogenerate -m "description"

# Create a new empty migration
alembic revision -m "description"
```

## Database Setup Checklist

Before running migrations:

- [ ] PostgreSQL is installed and running
- [ ] Database `ai_test_case_generator` is created
- [ ] Redis is installed and running
- [ ] Environment variables are configured in `.env`
- [ ] Python dependencies are installed (`pip install -r requirements.txt`)

## Troubleshooting

### Connection Error

If you get a connection error:
1. Check PostgreSQL is running: `pg_isready`
2. Verify database exists: `psql -l | grep ai_test_case_generator`
3. Check `.env` file has correct `DATABASE_URL`

### Migration Conflicts

If migrations fail due to conflicts:
1. Check current state: `alembic current`
2. View pending migrations: `alembic history`
3. Manually resolve conflicts in migration files
4. Try again: `alembic upgrade head`

### Reset Database

To completely reset the database:
```bash
# Drop all tables
alembic downgrade base

# Re-run all migrations
alembic upgrade head
```

Or drop and recreate the database:
```bash
dropdb ai_test_case_generator
createdb ai_test_case_generator
python scripts/init_db.py
```
