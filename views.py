import datetime as dt
import flask

import app
import db


@app.app.route('/ping')
def ping():
    return "pong"


@app.app.route('/museums', methods=['GET'])
def museums():
    museums = db.get_museums()
    return flask.render_template('museums.html', museums=museums)


@app.app.route('/museums/<int:id>', methods=['GET'])
def museums_id(id):
    museum_info = db.get_museum_by_id(id=id)
    return flask.render_template('museum.html', **museum_info)


@app.app.route('/museums/create', methods=['GET', 'POST'])
def museums_create():
    import models

    if flask.request.method == 'GET':
        cities = db.get_cities()
        return flask.render_template('museums_add.html', cities=cities)
    input = dict(**flask.request.form)
    if dt.datetime.fromisoformat(input['foundation_date']) > dt.datetime.now():
        raise app.exceptions.BadRequest("Невалидная дата")
    museum = models.Museum(
        id=db.generate_new_id_for_model(models.Museum),
        **input
    )
    db.insert_museum(museum)
    return flask.redirect('/museums')


@app.app.route('/persons', methods=['GET'])
def persons():
    persons = db.get_persons()
    return flask.render_template('persons.html', persons=persons)


@app.app.route('/persons/<int:id>', methods=['GET'])
def persons_id(id):
    person = db.get_person_by_id(id)
    return flask.render_template('person.html', **person)


@app.app.route('/persons/create', methods=['GET', 'POST'])
def person_create():
    import models

    if flask.request.method == 'GET':
        countries = db.get_countries()
        exhibits = db.get_exhibits()
        return flask.render_template('persons_add.html', countries=countries, exhibits=exhibits)

    input = dict(**flask.request.form)
    if dt.datetime.fromisoformat(input['birth_date']) > dt.datetime.now():
        raise app.exceptions.BadRequest("Невалидная дата")
    death = input.pop('death', None)
    countries = flask.request.form.getlist('countries')
    exhibits = flask.request.form.getlist('exhibits')
    input.pop('countries')
    input.pop('exhibits')
    person = models.Person(
        id=db.generate_new_id_for_model(models.Person),
        **input
    )
    if death:
        if input['birth_date'] >= death:
            raise app.exceptions.BadRequest("Невалидная дата")
        death = models.Death(
            id=person.id,
            death=death
        )
    db.insert_person(person, death, exhibits, countries)
    return flask.redirect('/persons')


@app.app.route('/', methods=['GET'])
def exhibits():
    exhibits = db.get_exhibits_full_info()
    return flask.render_template('exhibits.html', exhibits=exhibits)


@app.app.route('/exhibits/create', methods=['GET', 'POST'])
def exhibits_create():
    import models

    if flask.request.method == 'GET':
        museums = db.get_museums()
        persons = db.get_persons()
        return flask.render_template('exhibits_add.html', museums=museums, persons=persons)

    input = dict(**flask.request.form)
    if dt.datetime.fromisoformat(input['release_date']) > dt.datetime.now():
        raise app.exceptions.BadRequest("Невалидная дата")

    persons = flask.request.form.getlist('persons')
    input.pop('persons')
    exhibit = models.Exhibit(
        id=db.generate_new_id_for_model(models.Exhibit),
        **input
    )
    db.insert_exhibit(exhibit, persons)
    return flask.redirect('/')

