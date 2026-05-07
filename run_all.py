# ============================================================
# Script de Démarrage Complet MobiTranz
# Fichier : run_all.py
# Description : Démarre backend + seed data pour démonstration
# ============================================================

import subprocess
import time
import sys
import os

def start_backend():
    """Démarre le backend FastAPI."""
    print("🚀 Démarrage du backend MobiTranz...")
    
    # Set environment
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./mobitranz.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to be ready
    time.sleep(3)
    
    # Check if started
    import httpx
    try:
        resp = httpx.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Backend démarré sur http://localhost:8000")
            return proc
    except:
        pass
    
    print("⚠️ Backend peut avoir des erreurs, vérifiez les logs")
    return proc


def run_seed():
    """Exécute le seed data."""
    print("🌱 Chargement des données de demonstration...")
    
    try:
        result = subprocess.run(
            [sys.executable, "backend/scripts/seed.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ Données de démo chargées")
        else:
            print("⚠️ Seed peut avoir des erreurs")
    except Exception as e:
        print(f"⚠️ Erreur seed: {e}")


def start_desktop():
    """Démarre l'application desktop."""
    print("🖥️ Démarrage de l'application bureau...")
    
    proc = subprocess.Popen(
        [sys.executable, "desktop_admin/main.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env={**os.environ, "PYTHONPATH": os.path.dirname(os.path.abspath(__file__))}
    )
    return proc


if __name__ == "__main__":
    print("=" * 50)
    print("MobiTranz - Démarrage Complet")
    print("=" * 50)
    
    backend_proc = start_backend()
    
    if backend_proc:
        run_seed()
    
    print("\n" + "=" * 50)
    print("✅ Système MobiTranz prêt!")
    print("=" * 50)
    print("Endpoints disponibles:")
    print("  - API:        http://localhost:8000")
    print("  - Swagger:    http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("\nComptes de test:")
    print("  - Admin:      +24101020304 / AdminMobitranz2026!")
    print("  - Ministere:  +24103040506 / Ministere2026!")
    print("  - Chauffeur:  +24106010203 / DriverMobitranz2026!")
    print("\nAppuyez sur Ctrl+C pour arrêter")
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système...")
        backend_proc.terminate()
        print("✅ Arrêté")