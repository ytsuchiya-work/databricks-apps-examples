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

1. **PostgreSQL Database** (version 12 or higher)
   - Install PostgreSQL locally or use a cloud provider (AWS RDS, Google Cloud SQL, Azure Database, etc.)
   - Create a database for the application
   - Have connection credentials ready (host, port, username, password)

2. **Python 3.11+** and **uv** package manager
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

## Features

- 📊 **Excel-like Grid**: Edit data with AG-Grid's powerful interface
- 💾 **Database Writeback**: Persist changes directly to PostgreSQL
- 📈 **Forecast Management**: Submit and track forecast requests
- 🔄 **Real-time Updates**: Changes reflected immediately
- 📁 **CSV Upload**: Bulk import data from CSV files
- 🎨 **Modern UI**: Built with Dash Mantine Components

## Running Locally

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

4. Set up your PostgreSQL database:
   ```sql
   -- Connect to PostgreSQL and create database
   CREATE DATABASE dash_writeback;
   
   -- Connect to the new database
   \c dash_writeback
   
   -- Optional: Create a schema (if not using 'public')
   CREATE SCHEMA IF NOT EXISTS app_schema;
   ```

5. Configure environment variables:
   ```bash
   # Create a .env file
   touch .env
   ```
   
   Add the following to your `.env` file:
   ```bash
   # PostgreSQL Connection
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=dash_writeback
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_SCHEMA=public
   
   # Optional: Connection pool settings
   POSTGRES_POOL_SIZE=5
   POSTGRES_MAX_OVERFLOW=10
   ```

6. Load environment variables and run the app:
   ```bash
   # Load environment variables
   export $(grep -v '^#' .env | xargs)
   
   # Run the application
   uv run python -m dash_dbx_writeback.app
   ```

7. Open your browser and navigate to: `http://localhost:8050`

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

**Permission denied?**
- Ensure PostgreSQL user has proper permissions
- Run the verification script: `python setup_scripts/verify_setup.py`

**Connection issues?**
- Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check credentials in `.env` file
- Ensure firewall allows connections

**No data in app?**
- Run initialization script: `python setup_scripts/initialize_database.py`
- Check database has sample data: `SELECT COUNT(*) FROM layout_data;`

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
