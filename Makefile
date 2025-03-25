assign-conditions:
	pipenv run python -c "from scripts.assign_conditions import assign_conditions; assign_conditions()"

assign-product-for_rating:
	pipenv run python -c "from scripts.assign_product_for_rating import assign_proportion_based_product_for_rating; assign_proportion_based_product_for_rating()"

cloud-connect:
	gcloud compute ssh biasrecv2

create-model:
	pipenv run python -c "from scripts.train_recommender_model import create_recommender_model; create_recommender_model()"

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

start-rate:
	pipenv run python microapp.py --config=rate

update-deploy:
	git pull
	sudo supervisorctl stop microblog
	flask db upgrade
	sudo supervisorctl start microblog

send-files:
	gcloud compute scp --recurse deploy/data/to_send $(vm):datagotchi_sante/deploy/data/to_send
