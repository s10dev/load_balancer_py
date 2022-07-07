from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from pymemcache.client import base
import atexit
import socket
import time


HOST_NAME = socket.gethostname()

app = Flask(__name__)
# Инициализируем клиент мемкеша
memc_client = base.Client(('memcached', 11211))
memc_key = f'requests_in_proccess[{HOST_NAME}:5001]'
# В ключ пишем значение
memc_client.set(memc_key, 0)

# Функция логгирования текущих запросов в обработки
def log_current_requests_proccessing():
    date = datetime.now().strftime('[%d/%b/%Y %H:%M:%S] ')
    msg = date + 'Rps ~ ' + f'{int((memc_client.get(memc_key).decode("utf-8"))) // 10}'
    memc_client.set(memc_key, 0)
    print(msg)

# мини крон на функцию логгирования
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=log_current_requests_proccessing,
    trigger="interval",
    seconds=10
)
scheduler.start()

# декоратор для хендлера
# до процессинга функции инкремент ключа в мемкеше
# после декремент
def log_request_proccessing(func):
    def wrapper(*args, **kwargs):
        memc_client.incr(memc_key, 1)
        response = func(*args, **kwargs)
        return response
    return wrapper

# тестовый хендлер
@app.route('/')
@log_request_proccessing
def test():
    return f'Container ID: {HOST_NAME}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    # выключаем мини крон
    atexit.register(lambda: scheduler.shutdown())
