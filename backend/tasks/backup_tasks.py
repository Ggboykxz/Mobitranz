import structlog
import subprocess
import os

from backend.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=600, name="backup_tasks.run_backup")
def run_backup_task(self):
    script = os.path.join(os.getcwd(), "scripts", "backup.sh")
    if not os.path.exists(script):
        logger.warning("Script de sauvegarde non trouve", path=script)
        return {"status": "skipped", "reason": "backup.sh not found"}

    try:
        result = subprocess.run(
            ["bash", script],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            logger.info("Sauvegarde automatique reussie")
            return {"status": "success", "output": result.stdout}
        else:
            logger.error("Echec sauvegarde", stderr=result.stderr)
            return {"status": "failed", "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        logger.error("Timeout sauvegarde (5 min)")
        return {"status": "timeout"}
    except Exception as e:
        logger.error("Exception sauvegarde", error=str(e))
        raise self.retry(exc=e)
