from celery_tasks.main import app


@app.task
def send_sms_code(mobile, sms_code):
    #                      自己手机号       验证码 过期时间  短信模板
    from libs.yuntongxun.sms import CCP
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print('Celery验证码:', sms_code)
    return result
