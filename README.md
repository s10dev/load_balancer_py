FIRST TERMINAL:
```
docker-compose build && \
docker-compose up
```
SECOND TERMINAL:
```
python spam.py
```

THIRD TERMINAL:
```
sleep 100 && \
docker-compose pause app_1 && \
sleep 100 && \
docker-compose unpause app_1
```