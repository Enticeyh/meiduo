from apps.goods.models import SKU
from celery_tasks.main import app
from scripts.regenerate_detail_html import generate_static_sku_detail_html


@app.task
def get_detail_html(sku_id):
    sku = SKU.objects.get(id=sku_id)
    generate_static_sku_detail_html(sku)