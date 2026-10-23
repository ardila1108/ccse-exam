.PHONY: build run

APP_NAME = ccse-app
PORT = 8501

build:
	docker build -t $(APP_NAME) .

run:
	docker run -d -p $(PORT):8501 --name $(APP_NAME) $(APP_NAME)
	@echo "App is running at http://localhost:$(PORT)"

stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true
