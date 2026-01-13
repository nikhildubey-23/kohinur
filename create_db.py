from project import create_app, create_database

app = create_app()
create_database(app)
