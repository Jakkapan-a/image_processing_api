from flask import jsonify
from tabulate import tabulate
from app import create_app , db

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

@app.cli.command('drop-db')
def drop_db():
    """Drop the database."""
    with app.app_context():
        db.drop_all()
        print("Database tables dropped successfully!")

@app.cli.command('seed-db')
def seed_db():
    """Seed the database."""
    with app.app_context():
        from app.models.file_management import FileManagement
        db.session.add(FileManagement(name='test', filename='test.jpg', filepath='public/uploads/test.jpg', type_file='cls'))
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    # print routes
    route_list = []
    for rule in app.url_map.iter_rules():
        methods = ', '.join(sorted(rule.methods))
        route_list.append([rule.rule, methods, rule.endpoint])

    print(tabulate(route_list, headers=["Route", "Methods", "Endpoint"], tablefmt="grid"))

    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=app.config['PORT'])