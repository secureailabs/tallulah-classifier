# start local queue
docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 --network tallulah rabbitmq:3-management
# start local mongodb
docker run -d --rm --name mongo -p 27017:27017 --network tallulah mongo:6.0

# start main_test
python test/main_test.py