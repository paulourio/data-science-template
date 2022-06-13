.PHONY: test test_all
test:
	poetry run pytest -m "not slow" -vvv source

test_all:
	poetry run pytest -vvv source
