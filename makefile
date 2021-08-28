counter:
	pipenv run uvicorn counter:app --port 8282 --reload
gauge:
	pipenv run uvicorn gauge:app --port 8282 --reload
summary:
	pipenv run uvicorn summary:app --port 8282 --reload
histogram:
	pipenv run uvicorn histogram:app --port 8282 --reload