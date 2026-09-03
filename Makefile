.PHONY: install test run dashboard quality

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

run:
	python -m src.pipeline

dashboard:
	streamlit run app.py

quality:
	python -m compileall -q src app.py
	python -m pytest -q
