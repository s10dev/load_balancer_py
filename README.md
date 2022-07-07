docker-compose build && \
docker-compose up && \
python spam.py && \
sleep 100 && \
docker-compose pause app_1 && \
sleep 100 && \
docker-compose unpause app_1