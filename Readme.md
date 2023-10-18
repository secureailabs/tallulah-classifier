# start local queue
docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 --network tallulah rabbitmq:3-management
# start main_test
python test/main_test.py