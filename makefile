
build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules
PYTEST := pytest . --ignore=node_modules --cov=. --cov-config=.coveragerc --capture=no $(pytest_args) -vv
COLLECT_STATIC := python manage.py collectstatic --noinput
COMPILE_TRANSLATIONS := python manage.py compilemessages
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(COLLECT_STATIC) && $(COMPILE_TRANSLATIONS) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput && \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := python ./docker/env_writer.py ./docker/env.json ./docker/env.test.json

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export DIRECTORY_UI_SUPPLIER_API_CLIENT_CLASS_NAME=unit-test; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_API_CLIENT_API_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export DIRECTORY_UI_SUPPLIER_PORT=8005; \
	export DIRECTORY_UI_SUPPLIER_SECRET_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_DEBUG=true; \
	export DIRECTORY_UI_SUPPLIER_RECAPTCHA_PUBLIC_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_RECAPTCHA_PRIVATE_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export DIRECTORY_UI_SUPPLIER_GOOGLE_TAG_MANAGER_ENV=&gtm_auth=Ok4kd4Wf_NKgs4c5Z5lUFQ&gtm_preview=env-6&gtm_cookies_win=x; \
	export DIRECTORY_UI_SUPPLIER_ZENDESK_EMAIL=debug; \
	export DIRECTORY_UI_SUPPLIER_ZENDESK_SUBDOMAIN=debugdebugdebug; \
	export DIRECTORY_UI_SUPPLIER_ZENDESK_TOKEN=debug; \
	export DIRECTORY_UI_SUPPLIER_UTM_COOKIE_DOMAIN=.great; \
	export DIRECTORY_UI_SUPPLIER_THUMBNAIL_STORAGE_CLASS_NAME=local-storage; \
	export DIRECTORY_UI_SUPPLIER_THUMBNAIL_KVSTORE_CLASS_NAME=dummy; \
	export DIRECTORY_UI_SUPPLIER_NOCAPTCHA=true; \
	export DIRECTORY_UI_SUPPLIER_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_UI_SUPPLIER_SECURE_HSTS_SECONDS=0; \
	export DIRECTORY_UI_SUPPLIER_SECURE_SSL_REDIRECT=false; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_CMS_API_CLIENT_BASE_URL=http://cms.trade.great:8010; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_CMS_API_CLIENT_API_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_FORMS_API_BASE_URL=forms.trade.great:8011;\
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_FORMS_API_API_KEY=debug; \
	export DIRECTORY_UI_SUPPLIER_DIRECTORY_FORMS_API_SENDER_ID=debug; \
	export DIRECTORY_UI_SUPPLIER_FEATURE_DIRECTORY_FORMS_API_ENABLED=false; \
	export DIRECTORY_UI_SUPPLIER_CONTACT_SUPPLIER_FROM_EMAIL=test@example.com


docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS)

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep directoryui_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it directoryui_webserver_1 sh

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

docker_build:
	docker build -t ukti/directory-ui-supplier:latest .

DEBUG_SET_ENV_VARS := \
	export PORT=8005; \
	export SECRET_KEY=debug; \
	export DEBUG=true ;\
	export DIRECTORY_API_CLIENT_API_KEY=debug; \
	export DIRECTORY_API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export RECAPTCHA_PUBLIC_KEY=$$DIRECTORY_UI_SUPPLIER_RECAPTCHA_PUBLIC_KEY; \
	export RECAPTCHA_PRIVATE_KEY=$$DIRECTORY_UI_SUPPLIER_RECAPTCHA_PRIVATE_KEY; \
	export GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export GOOGLE_TAG_MANAGER_ENV=&gtm_auth=Ok4kd4Wf_NKgs4c5Z5lUFQ&gtm_preview=env-6&gtm_cookies_win=x; \
	export ZENDESK_EMAIL=""; \
	export ZENDESK_SUBDOMAIN=""; \
	export ZENDESK_TOKEN=debug; \
	export UTM_COOKIE_DOMAIN=.great; \
	export THUMBNAIL_STORAGE_CLASS_NAME=local-storage; \
	export THUMBNAIL_KVSTORE_CLASS_NAME=redis; \
	export REDIS_URL=redis://localhost:6379; \
	export NOCAPTCHA=true; \
	export SESSION_COOKIE_SECURE=false; \
	export SECURE_HSTS_SECONDS=0 ;\
	export SECURE_SSL_REDIRECT=false; \
	export DIRECTORY_CMS_API_CLIENT_BASE_URL=http://cms.trade.great:8010; \
	export DIRECTORY_CMS_API_CLIENT_API_KEY=debug; \
	export FEATURE_SEARCH_ENGINE_INDEXING_DISABLED=true; \
	export DIRECTORY_FORMS_API_BASE_URL=http://forms.trade.great:8011;\
	export DIRECTORY_FORMS_API_API_KEY=$$DIRECTORY_UI_SUPPLIER_DIRECTORY_FORMS_API_API_KEY; \
	export DIRECTORY_FORMS_API_SENDER_ID=$$DIRECTORY_UI_SUPPLIER_DIRECTORY_FORMS_API_SENDER_ID; \
	export FEATURE_DIRECTORY_FORMS_API_ENABLED=true; \
	export CONTACT_SUPPLIER_FROM_EMAIL=test@example.com


debug_webserver:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_WEBSERVER)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(COLLECT_STATIC) && $(COMPILE_TRANSLATIONS) && $(FLAKE8) && $(PYTEST) --cov-report=html

debug_test_last_failed:
	make debug_test pytest_args='--last-failed'

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

debug: test_requirements debug_test

heroku_deploy_dev:
	./docker/install_heroku_cli.sh
	docker login --username=$$HEROKU_EMAIL --password=$$HEROKU_TOKEN registry.heroku.com
	~/bin/heroku-cli/bin/heroku container:push web --app directory-ui-supplier-dev
	~/bin/heroku-cli/bin/heroku container:release web --app directory-ui-supplier-dev

integration_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_integration_tests

compile_requirements:
	python3 -m piptools compile requirements.in
	python3 -m piptools compile requirements_test.in

.PHONY: build clean test_requirements docker_run docker_debug docker_webserver_bash docker_test debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
