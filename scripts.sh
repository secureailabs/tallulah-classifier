#!/bin/bash
set -e
set -x

# Check if docker is installed
check_docker() {
    docker --version
    retVal=$?
    if [ $retVal -ne 0 ]; then
        echo "Error docker does not exist"
        exit $retVal
    fi
}

# function to tag and push the input image to the docker hub
push_image_to_registry() {
    # check docker installed
    check_docker
    az login

    # check if the DOCKER_REGISTRY_NAME is set
    if [ -z "$DOCKER_REGISTRY_NAME" ]; then
        echo "DOCKER_REGISTRY_NAME is not set"
        exit 1
    fi

    echo "login to azure account"
    az account set --subscription $AZURE_SUBSCRIPTION_ID

    echo "log in to azure registry"
    az acr login --name "$DOCKER_REGISTRY_NAME"

    # Get the version from the ../VERSION file
    version=$(cat VERSION)

    # Get the current git commit hash
    gitCommitHash=$(git rev-parse --short HEAD)

    echo "Tag and Pushing image to azure hub"
    tag=v"$version"_"$gitCommitHash"
    echo "Tag: $tag"
    docker tag "$1" "$DOCKER_REGISTRY_NAME".azurecr.io/"$1":"$tag"
    docker push "$DOCKER_REGISTRY_NAME".azurecr.io/"$1":"$tag"
    echo Image url: "$DOCKER_REGISTRY_NAME".azurecr.io/"$1":"$tag"
}

# Function to build image
build_image() {
    check_docker
    poetry export -f requirements.txt --output requirements.txt --without-hashes
    docker build -t $1 . --platform linux/amd64
}

# Run the docker image
run_image() {

    check_docker

    # Create a network if it doesn't exist
    if ! docker network ls | grep -q "tallulah"; then
        docker network create tallulah
    fi


    # Run the classifier image
    docker run -it --rm -v $(pwd)/app:/app --name classifier --env-file .env --network tallulah tallulah/classifier --platform linux/amd64
}


# Run the docker image
test_image() {

    build_image $1 

    # Create a network if it doesn't exist
    if ! docker network ls | grep -q "tallulah"; then
        docker network create tallulah
    fi


    # Run the classifier image
    docker run -it --rm -v $(pwd)/app:/app --name classifier --env-file .test_env --network tallulah tallulah/classifier
}

run() {
    cd app
    python3 main.py
}

# run whatever command is passed in as arguments
$@
