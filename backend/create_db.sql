-- LegalBridge database setup
-- Run as postgres superuser: psql -U postgres -f create_db.sql

CREATE USER legalbridge_user WITH PASSWORD 'changeme';
CREATE DATABASE legalbridge_db OWNER legalbridge_user;
GRANT ALL PRIVILEGES ON DATABASE legalbridge_db TO legalbridge_user;
