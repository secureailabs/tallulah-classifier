# repo overview
app/data, app/model, app/utils contain duplicate code that should be removed.

# build a model from the data
Ensure no containers are running
## start local mongodb
docker run -d --rm --name mongo -p 27017:27017 --network tallulah mongo:6.0
## load the training data from file into the database
python script/load_emails.py \
this requires
PATH_DIR_DATASET_RAW to be set to a folder that contains the tbbca folder which contains the csv files\
20231023_wwt_tags.csv\
20231031_wwt_tags.csv\
## build a model from the database



# Running local tests
Ensure no containers are running
## start local mongodb
docker run -d --rm --name mongo -p 27017:27017 --network tallulah mongo:6.0


## start main_test
python test/main_test.py




# Running local deployment
## build the image
make build_image

## start local queue
docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 --network tallulah rabbitmq:3-management
## start local mongodb
docker run -d --rm --name mongo -p 27017:27017 --network tallulah mongo:6.0
## start local app
docker run -it --rm --name classifier --env-file .env --network tallulah tallulah/classifier

