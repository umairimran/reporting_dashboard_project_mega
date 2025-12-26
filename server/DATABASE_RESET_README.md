# 🔥 DATABASE RESET TOOL

## ⚠️ WARNING

This tool will **COMPLETELY DELETE ALL DATA** from your database and recreate it from scratch!

**Use this ONLY when:**
- 💥 Database is corrupted
- 🔄 You need a fresh start
- 🧪 Testing/Development scenarios
- 🚨 Emergency database recovery

**DO NOT use in production with real customer data!**

---

## 📋 What It Does

1. ✅ Connects to your database (Docker or local)
2. 💀 **DROPS all tables** (destroys all data!)
3. 🏗️ Recreates schema from `database_schema.sql`
4. 👤 Creates default admin user
5. 🎉 Database is fresh and ready to use

---

## 🚀 Usage

### On Windows:

```batch
cd server
reset_database.bat
```

Or manually:
```batch
python reset_database.py
```

### On Linux/Mac/Ubuntu Server:

```bash
cd server
chmod +x reset_database.sh
./reset_database.sh
```

Or manually:
```bash
python3 reset_database.py
```

---

## 🔐 Safety Features

1. **Confirmation Required**: Script asks you to type `YES DELETE EVERYTHING` before proceeding
2. **Clear Warnings**: Red warning messages before any destructive action
3. **Detailed Output**: Shows exactly what it's doing at each step
4. **Error Handling**: Stops if anything goes wrong

---

## 📝 Example Output

```
======================================================================
                      DATABASE RESET TOOL
======================================================================

Database: localhost:5432/megaDB

⚠️  WARNING: This will DELETE ALL DATA in the database!
This action cannot be undone!

Type 'YES DELETE EVERYTHING' to confirm: YES DELETE EVERYTHING

Starting database reset...

→ Connecting to database...
✓ Connected successfully

→ Dropping all tables...
  - Dropping table: users
  - Dropping table: clients
  - Dropping table: campaigns
  - Dropping table: daily_metrics
  ...
✓ All tables dropped successfully

→ Recreating database schema...
✓ Database schema created successfully

→ Creating admin user...
✓ Admin user created
  Email: admin@gmail.com
  Password: admin123
  ⚠️  Change this password after first login!

======================================================================
                   DATABASE RESET COMPLETE
======================================================================

✓ Database has been completely reset!

Next steps:
  1. Start your backend server
  2. Login with admin@gmail.com / admin123
  3. Change the admin password
  4. Upload your data files
```

---

## 🔧 Requirements

1. **Database Running**: 
   - If using Docker: `docker-compose up -d`
   - If local PostgreSQL: Make sure it's started

2. **Environment Variables**:
   - `server/.env` must have correct `DATABASE_URL`
   - `POSTGRES_PASSWORD` must be set

3. **Python Dependencies**:
   ```bash
   pip install psycopg2-binary python-dotenv passlib bcrypt
   ```

---

## 🔍 Troubleshooting

### Error: "Cannot connect to database"

**Fix:**
```bash
# Start Docker database
docker-compose up -d db

# Wait 5 seconds
sleep 5

# Try again
python reset_database.py
```

### Error: "DATABASE_URL not found"

**Fix:**
Check `server/.env` has:
```bash
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/megaDB
POSTGRES_PASSWORD=YOUR_PASSWORD
```

### Error: "database_schema.sql not found"

**Fix:**
Make sure you're running from `server/` directory:
```bash
cd server
python reset_database.py
```

---

## 🎯 After Reset

1. **Login**: Use `admin@gmail.com` / `admin123`
2. **Change Password**: Security → Change Password
3. **Create Clients**: Admin → Clients → Add Client
4. **Upload Data**: Admin → Ingestion → Upload Files

---

## 💡 Alternative: Manual Reset via Docker

If you want to reset database using Docker Compose:

```bash
# Stop everything
docker-compose down

# Delete volumes (destroys data)
docker volume rm reporting_dashboard_project_mega_postgres_data

# Start fresh
docker-compose up -d
```

This recreates database from scratch using `database_schema.sql`.

---

## 🆘 Emergency Contact

If you have issues:
1. Check Docker logs: `docker logs reporting_db`
2. Check backend logs: `docker logs reporting_backend`
3. Verify .env file has all required variables
4. Make sure database port 5432 is not already in use

---

## ⚡ Quick Commands Cheat Sheet

```bash
# Windows
cd server && python reset_database.py

# Linux/Mac
cd server && python3 reset_database.py

# Check if database is running
docker ps | grep reporting_db

# View database logs
docker logs reporting_db

# Connect to database manually
docker exec -it reporting_db psql -U postgres -d megaDB
```

---

**Remember: This is a destructive operation! Always backup important data first!** 💾

