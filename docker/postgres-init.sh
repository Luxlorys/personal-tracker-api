#!/usr/bin/env bash
# Runs once, when the postgres data directory is first created.
# Creates the database the integration tests use.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-SQL
  CREATE DATABASE ${POSTGRES_DB}_test;
SQL
