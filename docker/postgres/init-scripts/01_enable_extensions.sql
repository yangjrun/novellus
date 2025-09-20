-- Enable required PostgreSQL extensions
-- This script runs automatically when the PostgreSQL container starts

-- Enable UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for text similarity
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable btree_gin for better indexing
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Create the database if it doesn't exist
SELECT 'CREATE DATABASE novellus'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'novellus')\gexec

-- Switch to novellus database
\c novellus;

-- Enable extensions in novellus database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;