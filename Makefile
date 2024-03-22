build : 
	docker build -t biasrecdocker .

develop : 
	 docker run -it -p 80:80 biasrecdocker bash

display-users:
	python -c "from scripts.view_databases import display_users; display_users()"

display-products:
	python -c "from scripts.view_databases import display_products; display_products()"

display-ratings:
	python -c "from scripts.view_databases import display_user_ratings; display_user_ratings()"

display-purchases:
	python -c "from scripts.view_databases import display_purchases; display_purchases()"

reload-experiment:
	pipenv run python -c "from scripts.reload_experiment import reload_databases; reload_databases()"
