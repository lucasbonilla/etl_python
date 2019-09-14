import pandas as pd
import requests
import json
from geopy import Point
from geopy.distance import distance, VincentyDistance


class MetaDados(object):
    geoposition = None
    bearing = None
    logradouro = None
    numero = None
    bairro = None
    cidade = None
    cep = None
    estado = None
    pais = None

    def __init__(self, latitude, longitude, distance=None, bearing=None, numero=None, bairro=None, cidade=None, cep=None, estado=None, pais=None):
        self.geoposition = Coordinates(latitude, longitude)
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.cep = cep
        self.estado = estado
        self.pais = pais
        if distance is not None and bearing is not None:
            self.bearing = Bearing(distance, bearing, latitude, longitude)


class Coordinates(object):
    latitude = None
    longitude = None

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def search_locale(self):
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=" + str(self.latitude) + "&lon=" + str(self.longitude))

        parsed_json = json.loads(r.text)
        if 'error' not in parsed_json:
            return parsed_json["place_id"]
        return None


class Bearing(object):

    distance = None
    bearing = None
    latitude = None
    longitude = None
    remote_geoposition = None

    def __init__(self, distance, bearing, latitude, longitude):
        self.distance = distance
        self.bearing = bearing
        self.latitude = latitude
        self.longitude = longitude
        self.remote_latitude, self.remote_longitude = self.calculate_remote_point()
        self.remote_geoposition = MetaDados(
            self.remote_latitude, self.remote_longitude)

    def calculate_remote_point(self):
        point = VincentyDistance(kilometers=self.distance).destination(
            Point(self.latitude, self.longitude), self.bearing)

        return point.latitude, point.longitude


def refactor(line):
    return line.lower().replace(" ", "")


def evaluate(coord, line):
    to_return = None
    if coord == 'la':
        if 's' in line:
            to_return = line.split('s')[1]
        elif 'n' in line:
            to_return = line.split('n')[1]
    elif coord == 'lo':
        if 'w' in line:
            to_return = line.split('w')[1]
        elif 'e' in line:
            to_return = line.split('e')[1]
    return to_return.replace("\n", "")


def distance_bearing(distance, bearing):
    # Distance: 2.2959 km  Bearing: 137.352°
    dist, bearing = line.split('km')
    dist = dist.split(':')[1].replace('.', '')
    bearing = bearing.split(':')[1].replace('°\n', '')
    return int(dist), float(bearing)


if __name__ == "__main__":
    # meta = MetaDados("-30.04982864", "-51.20150245")
    # print(meta.geoposition.search_locale())
    # br = Bearing(22959, 137.352, -30.04982864, -51.20150245)
    # print(br.remote_latitude)
    # print(br.remote_longitude)

    file_path = 'data/data_points_20180101.txt'
    latitude = []
    latitude_tmp = None
    longitude = []
    longitude_tmp = None
    distance = []
    distance_tmp = None
    bearing = []
    bearing_tmp = None
    places = []
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if line:
                line = refactor(line)
                if 'latitude' in line:
                    latitude_tmp = evaluate('la', line)
                elif 'longitude' in line:
                    longitude_tmp = evaluate('lo', line)
                else:
                    if not latitude_tmp or not longitude_tmp:
                        latitude_tmp = None
                        longitude_tmp = None
                        distance_tmp = None
                        bearing_tmp = None
                    else:
                        distance_tmp, bearing_tmp = distance_bearing(
                            'd_b', line)
                        latitude.append(latitude_tmp)
                        longitude.append(longitude_tmp)
                        distance.append(distance_tmp)
                        bearing.append(bearing_tmp)

            else:
                break

    for i in range(len(latitude)):
        places.append(MetaDados(latitude=latitude[i], longitude=longitude[i],
                                distance=distance[i], bearing=bearing[i]))

    for place in places:
        print(place)
