# voe-conosco

## Descrição

O projeto **voe-conosco** é uma aplicação Python que utiliza dados de voos em tempo real da API AviationStack para construir um grafo de rotas aéreas, permitindo encontrar o caminho mais barato entre aeroportos considerando restrições de tempo. Também integra a API Gemini para extração inteligente de códigos de aeroportos a partir de texto natural.

## Funcionalidades

- Consulta de voos em tempo real via AviationStack
- Construção de grafo temporal de rotas aéreas com NetworkX
- Visualização das rotas com Matplotlib
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
2. Execute o arquivo principal:
   ```bash
   python main.py
   ```
3. O programa irá:
   - Buscar voos e construir o grafo
   - Visualizar as rotas
   - Utilizar Gemini para extrair códigos de aeroportos
   - Calcular o caminho mais barato entre dois aeroportos

## Estrutura do Projeto

- `main.py`: código principal da aplicação
- `requirements.txt`: dependências do projeto
- `LICENSE`: licença de uso

## Observações

- Os preços das passagens são gerados aleatoriamente, pois a API não fornece valores reais.
- É necessário possuir chaves válidas das APIs para funcionamento completo.

## Licença

Este projeto está sob a licença MIT.
