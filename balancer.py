from flask import Flask, request, Response
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import configparser
import json


app = Flask(__name__)

APP_PORT = 5001

# Получаем список хостов из конфига
config = configparser.ConfigParser()
config.read('cfg.ini')
proxy_hosts_pool = json.loads(config['hosts_pool']['hosts'])
losted_hosts_pool = []

# Если бэкенд выбыл, полим его статус
# Если ответ 200 - добавляем в proxy_hosts_pool
def health_check_dead_hosts():
    for host in losted_hosts_pool:
        try:
            resp = requests.get(f'http://{host}:{APP_PORT}', timeout=0.5)
        except requests.exceptions.ReadTimeout:
            continue
        if resp.status_code == 200:
            losted_hosts_pool.remove(host)
            proxy_hosts_pool.append(host)
            print(f'Хост {host} снова в строю')


# мини крон на хелс чек упавших бекендов
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=health_check_dead_hosts,
    trigger="interval",
    seconds=5
)
scheduler.start()


# функция проксирования запроса к бэкенду
def _proxy(host, *args, **kwargs):
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host, host + f':{APP_PORT}'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        timeout=2)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    for host in proxy_hosts_pool:
        try:
            proxy_response = _proxy(host)
            # реализация паттерна Round robin
            proxy_hosts_pool.remove(host)
            proxy_hosts_pool.append(host)
            break
        # если хост мертвый, то вычеркиваем его из пула
        except requests.exceptions.ReadTimeout:
            print('Умер хост: ', host)
            proxy_hosts_pool.remove(host)
            losted_hosts_pool.append(host)
    # Если все хосты из пула мертвые, возвращаем 500-ку
    if 'proxy_response' not in locals():
        raise Exception('Нет доступных бэкендов')
    return proxy_response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
