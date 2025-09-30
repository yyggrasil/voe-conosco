# voe-conosco

## Descrição

O projeto **voe-conosco** é uma aplicação Python que utiliza dados de voos em tempo real da API AviationStack para construir um grafo de rotas aéreas, permitindo encontrar o caminho mais barato entre aeroportos considerando restrições de tempo para conexões. Também integra a API Gemini para extração inteligente de códigos de aeroportos a partir de texto natural.

## Funcionalidades

- Consulta de voos em tempo real via AviationStack
- Construção de grafo temporal de rotas aéreas com NetworkX
- Busca do caminho mais barato entre aeroportos usando Dijkstra
- Extração automática de códigos de aeroportos com Google Gemini

## Requisitos

Instale as dependências listadas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Como usar

1. Configure as variáveis de ambiente:
   - `AviationStack_api_key`: chave da API AviationStack
   - `GOOGLE_API_KEY`: chave da API Gemini
   - `SECRET_KEY`: chave secreta para o django
2. Rode as migrações do banco de dados
   ```bash
   python manage.py migrate
   ```
3. inicie o servidor Django:
   ```bash
   python manage.py runserver
   ```
3. O programa irá:
   - iniciar servidor web onde terá a pagina de admin no localhost/admin, onde será possivel visualizar os dados do banco
   - depois que o usuário escrevar seu plano de viagem o servidor irá calcular o caminho mais curto entre as viagens de avião

## Observações

- Os preços das passagens são gerados aleatoriamente, pois a API não fornece valores reais.
- É necessário possuir chaves válidas das APIs para funcionamento completo.

## Licença

Este projeto está sob nenhuma licença
