assign-conditions:
	pipenv run python -c "from scripts.assign_conditions import assign_conditions; assign_conditions()"

assign-product-for_rating:
	pipenv run python -c "from scripts.assign_product_for_rating import assign_proportion_based_product_for_rating; assign_proportion_based_product_for_rating()"

cloud-connect:
	gcloud compute ssh biasrecv2

create-similarity-matrix:
	pipenv run python -c "from scripts.create_model import create_similarity_matrix; create_similarity_matrix()"

create-predictions:
	pipenv run python -c "from scripts.create_model import create_predictions; create_predictions()"

create-recommendation:
	pipenv run python -c "from scripts.recommendation_pipeline.relative_multistakeholder import create_recommendations; create_recommendations()"

find-betas:
	pipenv run python -c "from scripts.multistakeholder_recommender import find_betas; find_betas()"

find-user-for-testing:
	pipenv run python -c "from scripts.multistakeholder_recommender import find_users_for_testing; find_users_for_testing()"


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

generate-trainset:
	pipenv run python -c "from scripts.generate_trainset import generate_trainset; generate_trainset()"

reload-experiment:
	pipenv run python -c "from scripts.reload_experiment import reload_databases; reload_databases()"

launch-fixedrec:
	pipenv run python microapp.py --config=fixedrec

launch-trainrec:
	pipenv run python microapp.py --config=trainrec

merge-ratings:
	pipenv run python -c "from scripts.merge_ratings import main; main()"

start-rate:
	pipenv run python microapp.py --config=rate

update-deploy:
	git pull
	sudo supervisorctl stop microblog
	flask db upgrade
	sudo supervisorctl start microblog

send-files:
	gcloud compute scp --recurse deploy/data/to_send $(vm):biasrec/deploy/data/to_send

download-files:
	gcloud compute scp --recurse $(vm):biasrec/deploy/data/received deploy/data/received 

start-deploy:
	sudo supervisorctl start microapp

stop-deploy:
	sudo supervisorctl stop microapp

dump-database:
	pipenv run python -c "from scripts.export_database import export_database_to_csv; export_database_to_csv()"

