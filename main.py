import pandas as pd
import requests
import json


class MetaDados(object):
    geoposition = None
    logradouro = None
    numero = None
    bairro = None
    cidade = None
    cep = None
    estado = None
    pais = None

    def __init__(self, latitude, longitude, numero=None, bairro=None, cidade=None, cep=None, estado=None, pais=None):
        self.geoposition = Coordinates(latitude, longitude)
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.cep = cep
        self.estado = estado
        self.pais = pais


class Coordinates(object):
    latitude = None
    longitude = None

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def search_locale(self):
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=" + self.latitude + "&lon=" + self.longitude)

        parsed_json = json.loads(r.text)
        return parsed_json["place_id"]


if __name__ == "__main__":
    meta = MetaDados("-30.04982864", "-51.20150245")
    print(meta.geoposition.search_locale())
