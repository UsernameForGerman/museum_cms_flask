import dataclasses as dc
import typing as tp


@dc.dataclass
class Museum:
    __tablename__ = 'museum'
    id: int
    name: str
    foundation_date: str
    city_id: int


@dc.dataclass
class City:
    __tablename__ = 'city'
    id: int
    name: str
    country_id: int


@dc.dataclass
class Country:
    __tablename__ = 'country'
    id: int
    name: str


@dc.dataclass
class Exhibit:
    __tablename__ = 'exhibit'
    id: int
    release_date: str
    title: str
    type: str
    museum_id: int


@dc.dataclass
class PersonToExhibit:
    __tablename__ = 'person_to_exhibit'
    exhibit_id: int
    person_id: int


@dc.dataclass
class Person:
    __tablename__ = 'person'
    id: int
    name: str
    birth_date: str


@dc.dataclass
class Death:
    __tablename__ = 'death'
    id: int
    death: str


@dc.dataclass
class CountryToPerson:
    __tablename__ = 'country_to_person'
    country_id: int
    person_id: int
