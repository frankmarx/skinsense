.PHONY: update-test-database update-prod-database

# Prompt for a migration message, then autogenerate + apply a migration
# against the TEST branch database (DB_URL from chalicelib/tests/.env.test).
update-test-database:
	@printf "Migration message: "; read -r MSG; \
	if [ -z "$$MSG" ]; then echo "Error: message is required"; exit 1; fi; \
	TEST_URL=$$(sed -n 's/^DB_URL=//p' chalicelib/tests/.env.test); \
	if [ -z "$$TEST_URL" ]; then echo "Error: DB_URL not set in chalicelib/tests/.env.test"; exit 1; fi; \
	HOST=$$(echo "$$TEST_URL" | sed -E 's#.*@([^/?]+).*#\1#'); \
	echo "Target: TEST branch ($$HOST)"; \
	DB_URL="$$TEST_URL" ./venv/bin/alembic revision --autogenerate -m "$$MSG" && \
	DB_URL="$$TEST_URL" ./venv/bin/alembic upgrade head

# Apply the newest migration revision to the PRODUCTION database
# (URL resolved from AWS Secrets Manager via chalicelib.utils.config.get_db_url).
# Asks for confirmation first.
update-prod-database:
	@PROD_HOST=$$(./venv/bin/python -c "from chalicelib.utils.config import get_db_url; print(get_db_url().split('@')[1])"); \
	echo "Target: PRODUCTION ($$PROD_HOST)"; \
	printf "Apply the newest migration to production? [y/N]: "; read -r CONFIRM; \
	if [ "$$CONFIRM" != "y" ] && [ "$$CONFIRM" != "Y" ]; then echo "Aborted."; exit 1; fi; \
	./venv/bin/alembic upgrade head && \
	./venv/bin/alembic current
