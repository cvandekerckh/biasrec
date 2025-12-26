import os
from datetime import datetime
import pandas as pd
from app import db
from app import create_app
from app.models import User, Product, Rating, purchases, training

app = create_app()

def export_database_to_csv():
    # Create timestamped directory
    now = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    export_dir = os.path.join('deploy', 'data', 'received', now)
    os.makedirs(export_dir, exist_ok=True)

    with app.app_context():

        # ---------- STANDARD EXPORTS (UNCHANGED) ----------
        tables = {
            'User': User,
            'Product': Product,
            'Rating': Rating,
            'Purchases': purchases,
            'Training': training,
        }

        for name, table in tables.items():
            if isinstance(table, db.Table):
                query = db.session.execute(table.select())
                df = pd.DataFrame(query.fetchall(), columns=query.keys())
            else:
                query = table.query.all()
                df = pd.DataFrame([row.__dict__ for row in query])
                df.drop(columns=['_sa_instance_state'], inplace=True, errors='ignore')

            df.to_csv(os.path.join(export_dir, f'{name}.csv'), index=False)

        # ---------- EXPORTS WITH PROLIFIC_PID ----------

        # Ratings + PROLIFIC_PID
        ratings_query = (
            db.session.query(
                Rating.user_id,
                User.code.label("prolific_pid"),
                Rating.product_id,
                Rating.rating
            )
            .join(User, User.id == Rating.user_id)
        )
        pd.read_sql(
            ratings_query.statement,
            db.engine
        ).to_csv(
            os.path.join(export_dir, "Rating_with_prolific_pid.csv"),
            index=False
        )

        # Training + PROLIFIC_PID
        training_query = (
            db.session.query(
                training.c.user_id,
                User.code.label("prolific_pid"),
                training.c.product_id
            )
            .join(User, User.id == training.c.user_id)
        )
        pd.read_sql(
            training_query.statement,
            db.engine
        ).to_csv(
            os.path.join(export_dir, "Training_with_prolific_pid.csv"),
            index=False
        )

        # Purchases + PROLIFIC_PID
        purchases_query = (
            db.session.query(
                purchases.c.user_id,
                User.code.label("prolific_pid"),
                purchases.c.product_id
            )
            .join(User, User.id == purchases.c.user_id)
        )
        pd.read_sql(
            purchases_query.statement,
            db.engine
        ).to_csv(
            os.path.join(export_dir, "Purchases_with_prolific_pid.csv"),
            index=False
        )

    print(f"Export completed! Files are in: {export_dir}")
