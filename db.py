import itertools
import typing as tp

import app
import models


def get_museums() -> tp.List[models.Museum]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        raw_museums = cursor.execute('SELECT * FROM museum')
        return [models.Museum(*raw_museum) for raw_museum in raw_museums]


def get_museum_by_id(id: int) -> tp.Dict[str, tp.Union[models.Museum, models.City, models.Country, tp.List[tp.Dict[str, tp.Union[models.Exhibit, models.Type]]]]]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        museums = cursor.execute("""
        SELECT
            m.id,
            m.name,
            m.foundation_date,
            m.city_id,
            ci.id,
            ci.name,
            ci.country_id,
            co.id,
            co.name,
            e.id,
            e.release_date,
            e.title,
            e.type_id,
            e.museum_id,
            t.id,
            t.name
        FROM museum m
        INNER JOIN city ci
            ON m.city_id = ci.id
        INNER JOIN country co
            ON ci.country_id = co.id
        LEFT JOIN exhibit e
            ON e.museum_id = m.id
        LEFT JOIN type t
            ON e.type_id = t.id
        WHERE m.id = ?;
        """, [id]).fetchall()
        if not museums:
            raise app.exceptions.NotFound()
        exhibits = []
        for museum in museums:
            exhibit = models.Exhibit(
                id=museum[9],
                release_date=museum[10],
                title=museum[11],
                type_id=museum[12],
                museum_id=museum[13]
            ) if museum[9] is not None else None
            if exhibit and exhibit not in exhibits:
                type = models.Type(
                    id=museum[14],
                    name=museum[15]
                )
                exhibits.append({'exhibit': exhibit, 'type': type})
        return {
            'museum': models.Museum(id=museums[0][0], name=museums[0][1], foundation_date=museums[0][2], city_id=museums[0][3]),
            'city': models.City(id=museums[0][4], name=museums[0][5], country_id=museums[0][6]),
            'country': models.Country(id=museums[0][7], name=museums[0][8]),
            'exhibits': exhibits
        }


def get_persons() -> tp.List[models.Person]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        raw_persons = cursor.execute('SELECT * FROM person')
        return [models.Person(*raw_person) for raw_person in raw_persons]


def get_person_by_id(id: int) -> tp.Dict[str, tp.Union[models.Person, models.Death, tp.List[tp.Union[models.Country, tp.Dict[str, tp.Union[models.Exhibit, models.Type]]]]]]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        persons = cursor.execute("""
        SELECT 
            p.id, 
            p.name,
            p.birth_date,
            d.id,
            d.death,
            c.id,
            c.name,
            e.id,
            e.release_date,
            e.title,
            e.type_id,
            e.museum_id,
            t.id,
            t.name
        FROM person p
        LEFT JOIN death d
            ON p.id = d.id
        INNER JOIN country_to_person ctp
            ON ctp.person_id = p.id
        INNER JOIN country c
            ON c.id = ctp.country_id
        LEFT JOIN person_to_exhibit pte
            ON pte.person_id = p.id
        LEFT JOIN exhibit e
            ON e.id = pte.exhibit_id
        LEFT JOIN type t
            ON e.type_id = t.id
        WHERE p.id = ?;
        """, [id]).fetchall()
        if not persons:
            raise app.exceptions.NotFound()
        countries, exhibits = [], []
        for person in persons:
            country = models.Country(
                id=person[5],
                name=person[6]
            )
            if country not in countries:
                countries.append(country)
            exhibit = models.Exhibit(
                id=person[7],
                release_date=person[8],
                title=person[9],
                type_id=person[10],
                museum_id=person[11]
            ) if person[7] is not None else None
            if exhibit and exhibit not in exhibits:
                type = models.Type(id=person[12], name=person[13])
                exhibits.append({'exhibit': exhibit, 'type': type})
        return {
            'person': models.Person(id=persons[0][0], name=persons[0][1], birth_date=persons[0][2]),
            'death': models.Death(id=persons[0][3], death=persons[0][4]) if persons[0][3] is not None else None,
            'countries': countries,
            'exhibits': exhibits
        }


def get_exhibits_full_info() -> tp.List[tp.Dict[str, tp.Union[models.Exhibit, models.Museum, tp.List[models.Person]]]]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        exhibits = cursor.execute("""
        SELECT 
            e.id, 
            e.release_date,
            e.title,
            e.type_id,
            e.museum_id,
            p.id,
            p.name,
            p.birth_date,
            m.id,
            m.name,
            m.foundation_date,
            m.city_id,
            t.id,
            t.name
        FROM exhibit e
        INNER JOIN type t
            ON e.type_id = t.id
        LEFT JOIN person_to_exhibit pte
            ON pte.exhibit_id = e.id
        LEFT JOIN person p
            ON p.id = pte.person_id
        INNER JOIN museum m
            ON m.id = e.museum_id
        ORDER BY e.id DESC;
        """).fetchall()
        if not exhibits:
            raise app.exceptions.NotFound()
        result = []
        for exhibit_id, grouped_exhibits in itertools.groupby(exhibits, key=lambda exhibit: exhibit[0]):
            exhibit_result = {}
            persons = []
            for exhibit in grouped_exhibits:
                exhibit_result.update({
                    'exhibit': models.Exhibit(
                        id=exhibit[0],
                        release_date=exhibit[1],
                        title=exhibit[2],
                        type_id=exhibit[3],
                        museum_id=exhibit[4],
                    ),
                    'type': models.Type(
                        id=exhibit[12],
                        name=exhibit[13]
                    )
                })
                exhibit_result.update({
                    'museum': models.Museum(
                        id=exhibit[8],
                        name=exhibit[9],
                        foundation_date=exhibit[10],
                        city_id=exhibit[11]
                    )
                })
                person = models.Person(
                    id=exhibit[5],
                    name=exhibit[6],
                    birth_date=exhibit[7]
                ) if exhibit[5] is not None else None
                if person and person not in persons:
                    persons.append(person)
            exhibit_result['persons'] = persons
            result.append(exhibit_result)
        return result


def get_exhibits() -> tp.List[models.Exhibit]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        return [models.Exhibit(*exhibit) for exhibit in cursor.execute(
            """
            SELECT * FROM exhibit;
            """
        )]


def generate_new_id_for_model(model: tp.Type[tp.Union[models.Museum, models.Death, models.Exhibit, models.Country, models.Person, models.City, models.PersonToExhibit, models.CountryToPerson]]) -> int:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        id = cursor.execute('SELECT id FROM {tablename} ORDER BY id DESC LIMIT 1;'.format(tablename=model.__tablename__)).fetchone()
        return id[0] + 1 if id else 0


def insert_museum(museum: models.Museum):
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO museum (id, name, foundation_date, city_id)
            VALUES (?, ?, ?, ?);
            """, [museum.id, museum.name, museum.foundation_date, museum.city_id]
        )


def insert_person(person: models.Person, death: models.Death, exhibits: tp.List[str], countries: tp.List[str]):
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO person (id, name, birth_date)
            VALUES (?, ?, ?);
            """, [person.id, person.name, person.birth_date]
        )
        if death:
            cursor.execute(
                """
                INSERT INTO death (id, death)
                VALUES (?, ?)
                """, [death.id, death.death]
            )
        cursor.executemany(
            """
            INSERT INTO country_to_person(country_id, person_id)
            VALUES (?, ?)
            """,
            [(country_id, person.id) for country_id in countries]
        )
        if exhibits:
            cursor.executemany(
                """
                INSERT INTO person_to_exhibit(person_id, exhibit_id)
                VALUES (?, ?)
                """,
                [(person.id, exhibit_id) for exhibit_id in exhibits]
            )


def insert_exhibit(exhibit: models.Exhibit, persons: tp.List[str]):
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO exhibit (id, release_date, title, type_id, museum_id)
            VALUES (?, ?, ?, ?, ?);
            """, [exhibit.id, exhibit.release_date, exhibit.title, exhibit.type_id, exhibit.museum_id]
        )
        cursor.executemany(
            """
            INSERT INTO person_to_exhibit(person_id, exhibit_id)
            VALUES (?, ?)
            """,
            [(person_id, exhibit.id) for person_id in persons]
        )


def get_countries() -> tp.List[models.Country]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        return [models.Country(*country) for country in cursor.execute(
            """
            SELECT * FROM country;
            """
        )]


def get_cities() -> tp.List[models.City]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        return [models.City(*city) for city in cursor.execute(
            """
            SELECT * FROM city;
            """
        )]


def get_types() -> tp.List[models.Type]:
    with app.sqlite3.connect(app.DBNAME) as conn:
        cursor = conn.cursor()
        return [models.Type(*type) for type in cursor.execute(
            """
            SELECT * FROM type;
            """
        )]
