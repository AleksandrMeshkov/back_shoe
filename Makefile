build:
	docker-compose --env-file .env -f docker-compose.yml --project-directory . up --build -d
