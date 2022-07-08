from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit
import socket


HOST_NAME = socket.gethostname()

app = Flask(__name__)

requests_in_proccess = 0
# Функция логгирования текущих запросов в обработки
def log_current_requests_proccessing():
    global requests_in_proccess
    date = datetime.now().strftime('[%d/%b/%Y %H:%M:%S] ')
    msg = date + 'Rps ~ ' + str(requests_in_proccess // 10)
    requests_in_proccess = 0
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
def log_request_proccessing(func):
    def wrapper(*args, **kwargs):
        global requests_in_proccess
        requests_in_proccess += 1
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
