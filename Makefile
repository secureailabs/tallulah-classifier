.PHONY: clean build_image

run:
	@./scripts.sh run

build_image:
	@./scripts.sh build_image tallulah/classifier

run_image:
	@./scripts.sh run_image tallulah/classifier

push_image: build_image
	@./scripts.sh push_image_to_registry tallulah/classifier
