install:
	pip install -e ".[dev]"

test:
	python3 -m pytest -v

lint:
	ruff check .

format:
	black .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete


docker-build:
	docker-compose build

docker-up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Services started."
	@echo ""
	@echo "Access points:"
	@echo "  - API Docs:  http://localhost:8000/docs"
	@echo "  - API:       http://localhost:8000"
	@echo "  - RabbitMQ:  http://localhost:15672 (guest/guest)"
	@echo "  - MongoDB:   mongodb://localhost:27017"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v
	docker system prune -f

status:
	docker-compose ps
