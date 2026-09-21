# Database Configuration
- Engine: PostgreSQL 15+
- Multi-AZ Support: Enabled via AWS RDS
- Migrations: Managed via standard DDL scripts or Alembic
- To execute locally: `psql -U postgres -d mydatabase -f schema.sql`
