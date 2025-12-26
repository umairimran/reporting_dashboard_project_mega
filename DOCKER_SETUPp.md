# Docker Setup - Quick Reference

## 🚀 Start

**Windows:**
```bash
start-docker.bat
```

**Mac/Linux:**
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**Or:**
```bash
docker-compose up --build
```

## 🛑 Stop

**Windows:**
```bash
stop-docker.bat
```

**Mac/Linux:**
```bash
./stop-docker.sh
```

**Or:**
```bash
docker-compose down
```

## 🔑 Admin Login

- **URL:** http://localhost:3000
- **Email:** admin@gmail.com
- **Password:** admin123

## 📍 URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔄 Rebuild

```bash
docker-compose up --build
```

## 🗑️ Reset Everything

```bash
docker-compose down -v
docker-compose up --build
```

