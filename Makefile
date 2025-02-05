
build:
	docker build -t local/labelbox-python:test .

test-staging: build
	docker run -it -v ${PWD}:/usr/src -w /usr/src \
		-e LABELBOX_TEST_ENVIRON="staging" \
		-e LABELBOX_TEST_API_KEY_STAGING=${LABELBOX_TEST_API_KEY_STAGING} \
		local/labelbox-python:test pytest $(PATH_TO_TEST) -svvx

test-prod: build
	docker run -it -v ${PWD}:/usr/src -w /usr/src \
		-e LABELBOX_TEST_ENVIRON="prod" \
		-e LABELBOX_TEST_API_KEY_PROD=${LABELBOX_TEST_API_KEY_PROD} \
		local/labelbox-python:test pytest $(PATH_TO_TEST) -svvx
