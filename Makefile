build: 
	docker build -t biasrecdocker .

create-model:
	pipenv run python -c "from scripts.train_recommender_model import create_recommender_model; create_recommender_model()"

develop: 
	docker run -it -p 80:80 biasrecdocker bash

display-users:
	pipenv run python -c "from scripts.view_databases import display_users; display_users()"

display-products:
	pipenv run python -c "from scripts.view_databases import display_products; display_products()"

display-ratings:
	pipenv run python -c "from scripts.view_databases import display_ratings; display_ratings()"

display-purchases:
	pipenv run python -c "from scripts.view_databases import display_purchases; display_purchases()"

display-assignments:
	pipenv run python -c "from scripts.view_databases import display_assignments; display_assignments()"

reload-experiment:
	pipenv run python -c "from scripts.reload_experiment import reload_databases; reload_databases()"
