# ============================================
# Code Quality Commands
# ============================================

.PHONY: format lint check

format:
	@echo "🎨 Formatting Python code with Black..."
	black . --line-length=100
	@echo "📦 Sorting imports with isort..."
	isort .
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting with Flake8..."
	flake8 .
	@echo "✅ Linting complete"

check:
	@echo "🧪 Running all code quality checks..."
	black --check . --line-length=100
	flake8 .
	isort --check .
	@echo "✅ All checks passed"

# ============================================
# Development Commands
# ============================================

.PHONY: dev-up dev-down dev-logs dev-restart dev-shell dev-db-shell

dev-up:
	docker-compose -f docker-compose.dev.yml up --build

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

dev-restart:
	docker-compose -f docker-compose.dev.yml restart web

dev-shell:
	docker-compose -f docker-compose.dev.yml exec web bash

dev-db-shell:
	docker-compose -f docker-compose.dev.yml exec db mysql -u petfeeder -ppetfeeder123 smart_pet_feeder

# ============================================
# Production Commands
# ============================================

.PHONY: build up down logs restart ps

build:
	docker-compose build --no-cache

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

ps:
	docker-compose ps

# ============================================
# Utility Commands
# ============================================

.PHONY: shell db-shell clean prune health

shell:
	docker-compose exec web bash

db-shell:
	docker-compose exec db mysql -u root -p smart_pet_feeder

clean:
	docker-compose down -v --remove-orphans

prune:
	docker system prune -af --volumes

health:
	@echo "🏥 Checking service health..."
	@docker-compose ps
	@echo "\n📊 Container stats:"
	@docker stats --no-stream $$(docker-compose ps -q)

# ============================================
# Database Commands
# ============================================

.PHONY: db-backup db-restore

db-backup:
	@echo "💾 Backing up database..."
	docker-compose exec db mysqldump -u root -p smart_pet_feeder > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup completed"

db-restore:
	@echo "📥 Restoring database..."
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T db mysql -u root -p smart_pet_feeder < $$backup_file
	@echo "✅ Restore completed"

# ============================================
# Testing Commands
# ============================================

.PHONY: test test-health

test:
	docker-compose exec web python -m pytest

test-health:
	@echo "🧪 Testing application health..."
	@curl -f http://localhost:8000/ || echo "❌ Health check failed"

# ============================================
# Help
# ============================================

.PHONY: help

help:
	@echo "Smart Pet Feeder - Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up        - Start development environment"
	@echo "  make dev-down      - Stop development environment"
	@echo "  make dev-logs      - View development logs"
	@echo "  make dev-shell     - Open shell in web container"
	@echo ""
	@echo "Production:"
	@echo "  make build         - Build production image"
	@echo "  make up            - Start production containers"
	@echo "  make down          - Stop production containers"
	@echo "  make logs          - View production logs"
	@echo "  make restart       - Restart containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Remove containers and volumes"
	@echo "  make prune         - Clean up Docker system"
	@echo "  make health        - Check service health"
	@echo "  make db-backup     - Backup MySQL database"
	@echo ""
