import os
from datetime import datetime
import pandas as pd
from app import db
from app import create_app
from app.models import User, Product, Rating, purchases, training

app = create_app()

# Import your models

# Define export function
def export_database_to_csv():
    # Create timestamped directory
    now = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    export_dir = os.path.join('deploy', 'data', 'received', now)
    os.makedirs(export_dir, exist_ok=True)

    with app.app_context():
        # Define your tables
        tables = {
            'User': User,
            'Product': Product,
            'Rating': Rating,
            'Purchases': purchases,
            'Training': training,
        }

        for name, table in tables.items():
            if isinstance(table, db.Table):
                # For association tables
                query = db.session.execute(table.select())
                df = pd.DataFrame(query.fetchall(), columns=query.keys())
            else:
                # For models
                query = table.query.all()
                df = pd.DataFrame([row.__dict__ for row in query])
                df.drop(columns=['_sa_instance_state'], inplace=True, errors='ignore')

            # Export to CSV
            output_path = os.path.join(export_dir, f'{name}.csv')
            df.to_csv(output_path, index=False)

    print(f"Export completed! Files are in: {export_dir}")
