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

display-answers1:
	pipenv run python -c "from scripts.view_databases import display_answers_survey1; display_answers_survey1()"

display-answers2:
	pipenv run python -c "from scripts.view_databases import display_answers_survey2; display_answers_survey2()"

exportation-csv:
	pipenv run python -c "from scripts.view_databases import export_data_to_csv; export_data_to_csv()"

reload-experiment:
	pipenv run python -c "from scripts.reload_experiment import reload_databases; reload_databases()"


delete-experiment:
	pipenv run python -c "from scripts.reload_experiment import delete_databases; delete_databases()"

send-to-vm:
	gcloud compute scp app/static/data/test-recommender/cosine_similarity_matrix_finale.xls biasrecv2:biasrec/app/static/data/test-recommender
	gcloud compute scp app/static/img/* biasrecv2:biasrec/app/static/img
	gcloud compute scp app/static/data/test-recommender/recom.csv biasrecv2:biasrec/app/static/data/test-recommender/recom.csv
