#! /bin/bash
celery -A celery_tasks.main worker -l info
