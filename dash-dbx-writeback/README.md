# Writeback Application with Dash AG-Grid and PostgreSQL

Author: [David O'Keeffe](https://www.linkedin.com/in/dgokeeffe/)

This is an example of reading and writing tables to a PostgreSQL database using Dash AG-Grid, one of the most powerful Javascript libraries for Tabular visualization on the market.

It includes the ability to add validation steps and show warnings for duplicate keys and missing inputs, and disable submitting the table if the validations aren't acceptable. It provides an "Microsoft Excel" like experience for users to do things like submit a request for a forecast.

It's a complete example for building sophisticated multi-page apps using the latest libraries in the Python ecosystem. This includes tools like `uv`, `pytest` (for TDD and automated unit tests), and modern PostgreSQL database patterns.

> **Note**: This application was migrated from Databricks Unity Catalog to PostgreSQL. See [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md) for details about the migration.


## 🚀 Quick Start

**New to this application?** Follow the complete setup guide:
👉 **[docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md)** 👈

### 5-Step Setup (15-20 minutes)
1. Install prerequisites (Python 3.11+, PostgreSQL, uv)
2. Clone repository and install dependencies
3. Configure environment variables  
4. Run `setup_scripts/initialize_database.py`
5. Start the application

**Result:** Production-ready application with PostgreSQL backend! 🎉

## Prerequisites

1. **Databricks Lakebase PostgreSQL**
   - Access to a Databricks workspace with Lakebase enabled
   - A Lakebase PostgreSQL instance created in your workspace
   - Databricks personal access token for authentication
   - Connection details (hostname, database name, username)

2. **Python 3.11+** and **uv** package manager
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Databricks CLI** (for authentication)
   ```bash
   # Install Databricks CLI
   pip install databricks-cli
   
   # Configure authentication
   databricks configure --token
   ```

## Features

- 📊 **Excel-like Grid**: Edit data with AG-Grid's powerful interface
- 💾 **Database Writeback**: Persist changes directly to PostgreSQL
- 📈 **Forecast Management**: Submit and track forecast requests
- 🔄 **Real-time Updates**: Changes reflected immediately
- 📁 **CSV Upload**: Bulk import data from CSV files
- 🎨 **Modern UI**: Built with Dash Mantine Components

## Running Locally

### Architecture Overview

This application **always connects to Databricks Lakebase PostgreSQL** - both when running locally and when deployed to Databricks Apps. The only difference is how credentials are provided:

- **Local Development**: You manually set environment variables in a `.env` file
- **Databricks Deployment**: Environment variables are automatically injected from the database resource

### Environment Configuration

The application uses **standard PostgreSQL environment variables** (`PGHOST`, `PGPORT`, etc.) that point to your Databricks Lakebase instance.

### Setup Steps

1. Clone this repo to your local machine:
   ```bash
   git clone https://github.com/databricks-solutions/databricks-apps-examples.git
   cd databricks-apps-examples/dash-dbx-writeback
   ```

2. Create and activate a Python virtual environment:
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   # Or for development with testing dependencies
   uv pip install -e ".[dev]"
   ```

4. Configure Databricks CLI authentication:
   ```bash
   # Install Databricks CLI if not already installed
   pip install databricks-cli
   
   # Configure authentication with your workspace
   databricks configure --token
   # Enter your workspace URL and personal access token when prompted
   ```

5. Get your Lakebase instance name:
   
   Navigate to your Databricks workspace:
   1. Go to **SQL** → **Databases** (or check your Lakebase configuration)
   2. Find your Lakebase database instance name
   3. Note down the instance name (e.g., `daveok`, `my-instance`)

6. Configure environment variables for local development:
   ```bash
   # Copy the example environment file
   cp example.env .env
   ```
   
   Edit `.env` and set your instance name:
   ```bash
   # Just set the instance name - everything else is auto-populated!
   LAKEBASE_INSTANCE_NAME=your-instance-name
   
   # Optional: Override default database name
   LAKEBASE_DATABASE=databricks_postgres
   
   # Optional: Set schema (defaults to public)
   LAKEBASE_SCHEMA=public
   ```
   
   That's it! The application will automatically use WorkspaceClient to:
   - Get your username from `w.current_user.me().user_name`
   - Get the host from `w.database.get_database_instance(name=instance_name).read_write_dns`
   - Generate OAuth tokens automatically for secure connections
   
   > See `example.env` for detailed documentation and advanced configuration options

7. Load environment variables and run the app:
   ```bash
   # Load environment variables
   export $(grep -v '^#' .env | xargs)
   
   # Run the application
   uv run python -m dash_dbx_writeback.app
   ```

8. Open your browser and navigate to: `http://localhost:8050`

### How It Works

**Local Development (Simplified):**
- You only set `LAKEBASE_INSTANCE_NAME` in your `.env` file
- WorkspaceClient automatically populates:
  - `PGUSER` from `w.current_user.me().user_name`
  - `PGHOST` from `w.database.get_database_instance(name=instance_name).read_write_dns`
  - `PGDATABASE` defaults to `databricks_postgres`
- OAuth tokens are automatically generated and rotated via `RotatingTokenConnection`
- Databricks CLI handles authentication (set up via `databricks configure --token`)

**Databricks Deployment:**
- The `app.yml` references the `postgres-database` resource
- Databricks automatically injects `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`
- The config detects these variables and uses them directly
- OAuth tokens are generated using the app's service principal
- No need to set `LAKEBASE_INSTANCE_NAME` in production

### Important Notes

- **Single Source of Truth**: The application always uses the same Databricks Lakebase instance
- **No Local PostgreSQL Needed**: You don't need to run PostgreSQL locally - just connect to Lakebase
- **OAuth Authentication**: The app uses OAuth tokens instead of passwords for secure authentication
- **Automatic Token Rotation**: Tokens are generated fresh for each connection and automatically rotated
- **Development/Production Parity**: Same database in both environments ensures consistency

> [!NOTE]
> - The application will automatically create required tables on first run
> - Tables will be initialized with sample data if they don't exist  
> - See [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md) for detailed setup instructions
> - See [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md) for migration from Databricks

## 📂 Project Structure

```
dash-dbx-writeback/
├── config.py                    # Centralized configuration (dataclass-based)
├── database_setup/              # SQL schema files and documentation
│   ├── complete_schema_setup.sql
│   └── README.md
├── setup_scripts/               # Automated setup and verification scripts
│   ├── initialize_database.py
│   └── verify_setup.py
├── docs/                        # Comprehensive documentation
│   ├── SETUP-GUIDE.md          # **START HERE** - Complete setup guide
│   └── ARCHITECTURE.md          # Technical architecture overview
└── src/dash_dbx_writeback/     # Application source code
    ├── app.py                   # Main Dash application
    ├── database_operations.py   # Centralized database operations
    ├── callbacks/               # Event handlers
    ├── components/              # Reusable UI components
    ├── pages/                   # Multi-page application pages
    ├── config/                  # Configuration modules
    ├── data/                    # Sample data generation
    └── ml/                      # Machine learning modules
```

## 📚 Documentation

- **[docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md)** - **START HERE** - Complete step-by-step setup ⭐
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture and design
- **[database_setup/README.md](database_setup/README.md)** - Database schema details
- **[POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md)** - Migration guide from Databricks

## 🆘 Troubleshooting

**`PGHOST not set` error?**
- Create a `.env` file with your Databricks Lakebase connection details
- Ensure all required `PG*` environment variables are set
- Load environment variables: `export $(grep -v '^#' .env | xargs)`

**Connection issues?**
- Verify Databricks workspace is accessible
- Check your personal access token is valid
- Ensure Lakebase instance is running in your workspace
- Verify `PGHOST` points to your Lakebase instance hostname

**OAuth/Authentication errors?**
- Run `databricks configure --token` to authenticate
- Verify `DATABRICKS_HOST` and `DATABRICKS_TOKEN` in `.env`
- Check your Databricks user has access to the Lakebase instance

**Permission denied?**
- Ensure your Databricks user has `CAN_CONNECT_AND_CREATE` permission on the database
- Check schema permissions for the configured `LAKEBASE_SCHEMA`

**No data in app?**
- Run initialization script: `python setup_scripts/initialize_database.py`
- Check database has sample data via Databricks SQL Editor

See **[docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md)** for detailed troubleshooting

---

&copy; 2025 Databricks, Inc. All rights reserved. The source in this repository is provided subject to the Databricks License [https://databricks.com/db-license-source]. All included or referenced third party libraries are subject to the licenses set forth below.

| library                  | description                                        | license      | source                                              |
| ------------------------ | -------------------------------------------------- | ------------ | --------------------------------------------------- |
| dash                     | Framework for building analytical web applications | MIT          | https://github.com/plotly/dash                      |
| dash-ag-grid             | AG Grid Plugin for Dash apps                       | MIT          | https://github.com/plotly/dash-ag-grid              |
| dash_mantine_components  | Mantine components for Dash                        | MIT          | https://github.com/snehilvj/dash-mantine-components |
| pandas                   | Data analysis and manipulation library             | BSD 3-Clause | https://github.com/pandas-dev/pandas                |
| psycopg2-binary          | PostgreSQL adapter for Python                      | LGPL         | https://github.com/psycopg/psycopg2                 |
| SQLAlchemy               | SQL toolkit and ORM for Python                     | MIT          | https://github.com/sqlalchemy/sqlalchemy            |

Databricks support doesn't cover this content. For questions or bugs, please open a github issue and the team will help on a best effort basis.

---

## Questions and issues
Please file an issue on this repository when and if you run into errors with the deployed applications. Thanks!
