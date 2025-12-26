@echo off
echo.
echo Starting Reporting Dashboard Backend...
echo.
echo This will:
echo   - Create PostgreSQL database
echo   - Initialize database schema
echo   - Create admin user (admin@gmail.com / admin123)
echo   - Start backend API (http://localhost:8000)
echo.
echo Your frontend is on Vercel - no need to start it locally!
echo.
echo Press Ctrl+C to stop all services
echo.

docker-compose up --build

echo.
echo All services stopped
pause

