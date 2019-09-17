Esse ambiente utiliza um virtualenv chamado venv

Para rodar utilize
> virtuaenv venv

Para iniciar o ambiente virtual navegue até a raiz da aplicação e utilize
> source venv/bin/activate

Instale as dependências da aplicação com
> pip install -r requirements.txt


Nesta solução foi utilizado uma base de dados SQLite denominada "datapoints.db".

Para criar a base de dados deve ser executado o seguinte comando passando o caminho para o 
> python my_repository/manage.py version_control sqlite:///db/datapoints.db my_repository

Para inicializar a base de dados basta rodar o comando abaixo:
> migrate manage manage.py --repository=my_repository --url=sqlite:///db/datapoints.db

Onde no parâmetro --url é o caminho para a base de dados que será usada.

Após definido o caminho da base de dados basta rodar o comando abaixo para inicializar a base de dados
> python manage.py upgrade

O arquivo pressets.py contém as referências para as variáveis utilizadas na solução proposta:

- API_KEY: Chave de acesso para a API de consulta dos pontos geográficos
- API: endpoint da API de consulta dos pontos geográficos. Utilizar %s nos dados inputáveis. Exemplo: "https://us1.locationiq.com/v1/reverse.php?key=%s&lat=%s&lon=%s&format=json"
- DB: caminho para a base de dados a ser utilizada
- CHUNK: Tamanho do chunk para consulta. Será o passo utilizado para criação das n threads do sistema
- SLEEP_TIME: Tempo entre cada iteração para consultar a API
- FILE: Caminho para o arquivo a ter os dados enriquecidos

Como a proposta deveria ser desenvolvida apenas com opções OpenSource optou-se a utilizar uma API de acesso livre e gratuíto.
A API do site https://locationiq.com utiliza o OpenStreetMap para buscar pontos de interesse e possui uma taxa de acesso restrito.
Dessa forma, foi necessário utilizar um recurso para não extrapolar o número de requisições simultâneas da API.
Assim, o parâmetro SLEEP_TIME foi utilizado com o tempo de 0.09 segundos entre uma requisição e outra.
Para que não ocrressem acessos simultâneos na API foi necessário também sincronizar as N threads para que não ocorressem acessos sobrepostos.
A eficiencia com essa estratégia é muito abaixo das espectativas pois se forem feitas um milhão de consultas, com o tempo de 1 segundo entre elas
demoraria cerca de uma semana para que todos os cálculos fossem concluídos.

Com uma API mais robusta, como o Google Maps API certamente esse tempo cairia drasticamente.

Caso a API que será utilizada tenha essa opção de acessos simultâneos o SLEEP_TIME pode ser suprimido passando o valor 0 (zero) em no arquivo pressets.py


Referências:
- <https://www.code-learner.com/python-read-big-file-example/>
- <https://www.digitalocean.com/community/tutorials/how-to-index-and-slice-strings-in-python-3>
- <https://www.w3schools.com/python/ref_string_replace.asp>
- <https://www.movable-type.co.uk/scripts/latlong.html>
- <https://github.com/geopy/geopy>
- <http://alissonmachado.com.br/python-threads/>
- <https://stackoverflow.com/questions/509211/understanding-slice-notation>
