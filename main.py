import pandas as pd
import requests
import json
import presets
from geopy import Point
from geopy.distance import distance, geodesic
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import threading
import time

Base = declarative_base()
DBSession = scoped_session(sessionmaker())
engine = None

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

    def __init__(self, latitude, longitude, distance=None, bearing=None, numero=None, logradouro=None, bairro=None, cidade=None, cep=None, estado=None, pais=None):
        self.geoposition = Coordinates(latitude, longitude)
        self.numero = numero
        self.logradouro = logradouro
        self.bairro = bairro
        self.cidade = cidade
        self.cep = cep
        self.estado = estado
        self.pais = pais
        if distance is not None and bearing is not None:
            self.bearing = Bearing(distance, bearing, latitude, longitude)

    def add_informations(self):
        # preenche informações sobre o local buscando em uma API externa
        infos = self.geoposition.search_local()
        self.logradouro = infos['logradouro']
        self.numero = infos['numero']
        self.bairro = infos['bairro']
        self.cidade = infos['cidade']
        self.cep = infos['cep']
        self.estado = infos['estado']
        self.pais = infos['pais']

    def print_information(self):
        print(
            "Latitude: %s\nLongitude: %s" % (self.geoposition.latitude, self.geoposition.longitude)
        )


class Coordinates(object):
    latitude = None
    longitude = None

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def search_local(self):
        # busca infromações em uma API externa
        url = presets.API % (str(presets.API_KEY), str(self.latitude), str(self.longitude))
        r = requests.get(url)
        # carrega a resposta em um dicionário
        parsed_json = json.loads(r.text)
        if 'error' not in parsed_json and parsed_json is not None:
            return {
                "numero": parsed_json["address"]["house_number"] if "house_number" in parsed_json["address"].keys() else 0,
                "logradouro": (parsed_json["address"]["road"] if "road" in parsed_json["address"].keys() else None),
                "bairro": (parsed_json["address"]["suburb"] if "suburb" in parsed_json["address"].keys() else None),
                "cidade": (parsed_json["address"]["city"] if "city" in parsed_json["address"].keys() else None),
                "cep": (parsed_json["address"]["postcode"] if "postcode" in parsed_json["address"].keys() else None),
                "estado": (parsed_json["address"]["state"] if "state" in parsed_json["address"].keys() else None),
                "pais": (parsed_json["address"]["country"] if "country" in parsed_json["address"].keys() else None)
            }
        return None


class Bearing(object):

    # classe para calcular o ponto extremo indicado pelo bearing e distância de cada entrada

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
        # definição dos metadados do ponto remoto
        # esse ponto também pode ter suas inforações calculadas através do método search_local da classe Coordinates
        self.remote_geoposition = MetaDados(
            self.remote_latitude, self.remote_longitude)

    def calculate_remote_point(self):
        # função que calcula a latitude e longitude do ponto remoto indicado pela distância e bearing
        point = geodesic(kilometers=self.distance).destination(
            Point(self.latitude, self.longitude), self.bearing)

        return point.latitude, point.longitude


def refactor(line):
    # remove os espaços em branco de uma linha
    return line.lower().replace(" ", "")


def evaluate(coord, line):
    # limpa todos os tipos de caracteres e retorna longitude ou latitude conforme o que for passado em coord
    to_return = None
    if coord == 'la':
        if 's' in line:
            to_return = line.split('s')[1] # hemisfério sul
        elif 'n' in line:
            to_return = line.split('n')[1] # hemisfério norte
    elif coord == 'lo':
        if 'w' in line:
            to_return = line.split('w')[1] # hemisfério ocidental
        elif 'e' in line:
            to_return = line.split('e')[1] # hemisfério oriental
    return to_return.replace("\n", "")


def distance_bearing(distance, bearing):
    # limpa todos os tipos de caracteres e separa tanto distância quanto bearing da linha
    dist, bearing = line.split('km')
    dist = dist.split(':')[1].replace('.', '')
    bearing = bearing.split(':')[1].replace('°\n', '')
    return int(dist), float(bearing)

def thread_location(thread_id, data=None):
    print("thread %s" % thread_id)
    for i in range(len(data)):
        data[i].add_informations()
        data[i].print_information()
        time.sleep(presets.SLEEP_TIME)
        

    DBSession.bulk_save_objects(
        [
            Datapoints(latitude=data[i].geoposition.latitude, longitude=data[i].geoposition.longitude, numero=data[i].numero, bairro=data[i].bairro, cidade=data[i].cidade, estado=data[i].estado, cep=data[i].cep, pais=data[i].pais, logradouro=data[i].logradouro)
            for i in range(len(data))
        ]
    )
    DBSession.commit()

class Datapoints(Base):
    __tablename__ = "datapoints"

    id          = Column('id', Integer, primary_key=True)
    latitude    = Column('latitude', String(20))
    longitude   = Column('longitude', String(20))
    numero      = Column('numero', Integer)
    logradouro  = Column('logradouro', String(100))
    bairro      = Column('bairro', String(50))
    cidade      = Column('cidade', String(30))
    estado      = Column('estado', String(30))
    cep         = Column('cep', Integer)
    pais        = Column('pais', String(20))
    pais_codigo = Column('pais_codigo', String(2))


def init_sqlalchemy(dbname=presets.DB):
    global engine
    engine = create_engine(dbname, echo=False)
    DBSession.remove()
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":

    file_path = presets.FILE
    latitude = []
    latitude_tmp = None
    longitude = []
    longitude_tmp = None
    distance = []
    distance_tmp = None
    bearing = []
    bearing_tmp = None
    places = []
    with open(file_path, 'r') as f: # abre o arquivo para leitura
        while True:
            line = f.readline() # Lê cada linha do arquivo
            if line:
                line = refactor(line) # limpa a linha para poder ser realizada a varredura
                if 'latitude' in line: # se a linha contém a palavra 'latitude'
                    latitude_tmp = evaluate('la', line)
                elif 'longitude' in line: # senão, se a linha contém a palavra 'longitude'
                    longitude_tmp = evaluate('lo', line)
                else: # senão
                    if latitude_tmp is None or longitude_tmp is None: # se longitude e latitude não existem
                        # esse trecho é necessário pois existem alguns grupos no arquivo que não possuem ou latitude ou longitude
                        # para essas entradas elas foram ignoradas
                        latitude_tmp = None
                        longitude_tmp = None
                        distance_tmp = None
                        bearing_tmp = None
                    else: # caso longitude e latitude existam
                        #faz a captura dos dados e os adiona em um array cada um dos tipos
                        distance_tmp, bearing_tmp = distance_bearing(
                            'd_b', line)
                        latitude.append(latitude_tmp)
                        longitude.append(longitude_tmp)
                        distance.append(distance_tmp)
                        bearing.append(bearing_tmp)

            else:
                break

    # adiciona todas as informações na estrutura de dados MetaDados e adiciona em um array
    for i in range(len(latitude)):
        places.append(MetaDados(latitude=latitude[i], longitude=longitude[i],
                                distance=distance[i], bearing=bearing[i]))

    n = len(places)

    iteration = 1

    # instancia a base de dados
    init_sqlalchemy()

    # se o tamanho do array é menor que o chunk definido insere em apenas uma thread
    if n <= presets.CHUNK:
        t = threading.Thread(target=thread_location, args=(1, places))
        t.start()
    else:
        for chunk in range(0, n, presets.CHUNK):
            if chunk + presets.CHUNK < n:
                # corta o array em pedaços do tamanho do chunk
                place_slice = places[slice(chunk, chunk+presets.CHUNK)]
                t = threading.Thread(target=thread_location, args=(iteration, place_slice))
                iteration+=1
                t.start()
                # se existe um SLEEP_TIME aguarda o término de uma thread para começar a outra
                if presets.SLEEP_TIME:
                    t.join()
            else:
                # se ainda existe posições no array places eles serão passados para a última thread
                place_slice = places[slice(chunk, n)]
                t = threading.Thread(target=thread_location, args=(iteration, place_slice))
                iteration+=1
                t.start()
                if presets.SLEEP_TIME:
                    t.join()
                # encerra a execução do código de refinamento de dados
                break
