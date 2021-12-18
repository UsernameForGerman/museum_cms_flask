import sqlite3

from flask import Flask
from flask_bootstrap import Bootstrap
from werkzeug import exceptions


app = Flask(__name__)
app.url_map.strict_slashes = False
Bootstrap(app)
DBNAME = 'main.db'


def prepare_db():
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    statements = [
        """
        CREATE TABLE IF NOT EXISTS country(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS city(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            name TEXT,
            country_id INTEGER NOT NULL,
            FOREIGN KEY (country_id) REFERENCES country(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS museum(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            foundation_date TEXT NOT NULL,
            city_id INTEGER NOT NULL,
            FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS exhibit(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            release_date TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            museum_id INTEGER NOT NULL,
            FOREIGN KEY (museum_id) REFERENCES museum(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS person(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            birth_date TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS death(
            id INTEGER UNIQUE NOT NULL PRIMARY KEY,
            death DATE NOT NULL,
            FOREIGN KEY (id) REFERENCES person(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS person_to_exhibit(
            person_id INTEGER NOT NULL,
            exhibit_id INTEGER NOT NULL,
            FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE,
            FOREIGN KEY (exhibit_id) REFERENCES exhibit(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS country_to_person(
            country_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            FOREIGN KEY (country_id) REFERENCES country(id) ON DELETE CASCADE,
            FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS country_to_person_country_id_idx 
        ON country_to_person(country_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS country_to_person_person_id_idx
        ON country_to_person(person_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS person_to_exhibit_person_id_idx
        ON person_to_exhibit(person_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS person_to_exhibit_exhibit_id_idx
        ON person_to_exhibit(exhibit_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS museum_city_id_idx
        ON museum(city_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS city_country_id_idx
        ON city(country_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS exhibit_museum_id_idx
        ON exhibit(museum_id);
        """
    ]
    for statement in statements:
        cursor.execute(statement)


if __name__ == "__main__":

    # Need to make sure Flask knows about its views before we run
    # the app, so we import them. We could do it earlier, but there's
    # a risk that we may run into circular dependencies, so I do it at the
    # last minute here.

    from views import *

    prepare_db()
    app.app.run(debug=True, host='0.0.0.0', port=5024)  # 0.0.0.0 означает «все адреса IPv4 на локальном компьютере».
