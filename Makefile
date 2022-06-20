.PHONY: test test_all
test:
	poetry run pytest -m "not slow" source

test_all:
	poetry run pytest source
