import requests
from random import randint
import pandas as pd
import re
import os
import networkx as nx
from networkx.algorithms.shortest_paths.weighted import dijkstra_path
import matplotlib.pyplot as plt
import google.generativeai as genai

class FlightSearch:
    def __init__(self, df_flights=None):
        self.api_key = os.getenv('AviationStack_api_key')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.url = "http://api.aviationstack.com/v1/flights"
        self.df_flights = df_flights
        self.time_aware_graph = None
        self.gemini_model = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Inicializa o modelo Gemini para processamento de linguagem natural"""
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')

    def fetch_flights(self):
        """Busca dados de voos da API AviationStack"""
        params = {'access_key': self.api_key}
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            data = response.json()
            
            flight_list = []
            if 'data' in data and data['data']:
                for flight in data['data']:
                    flight_data = self._extract_flight_data(flight)
                    if all(flight_data.values()):
                        flight_list.append(flight_data)
            
            self.df_flights = pd.DataFrame(flight_list)
            self._process_flight_data()
            return self.df_flights
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from AviationStack API: {e}")
            print("Please ensure your API key is correct and you are subscribed to the service.")
            return None

    def _extract_flight_data(self, flight):
        """Extrai dados relevantes de um voo"""
        return {
            'flight_iata': flight.get('flight', {}).get('iata', ''),
            'flight_icao': flight.get('flight', {}).get('icao', ''),
            'airline_name': flight.get('airline', {}).get('name'),
            'airline_iata': flight.get('airline', {}).get('iata', ''),
            'airline_icao': flight.get('airline', {}).get('icao', ''),
            'flight_number': flight.get('flight', {}).get('number'),
            'departure_airport': flight.get('departure', {}).get('airport'),
            'departure_scheduled': flight.get('departure', {}).get('scheduled'),
            'departure_iata': flight.get('departure', {}).get('iata'),
            'arrival_airport': flight.get('arrival', {}).get('airport'),
            'arrival_iata': flight.get('arrival', {}).get('iata'),
            'arrival_scheduled': flight.get('arrival', {}).get('scheduled'),
            'status': flight.get('flight_status', 'scheduled'),
            'preco': randint(0, 100000) / 100  # Preço simulado
        }

    def _process_flight_data(self):
        """Processa os dados dos voos para análise"""
        if self.df_flights is not None and not self.df_flights.empty:
            self.df_flights['departure_scheduled'] = pd.to_datetime(self.df_flights['departure_scheduled'])
            self.df_flights['arrival_scheduled'] = pd.to_datetime(self.df_flights['arrival_scheduled'])
            
            # Mostra os primeiros registros processados
            processed = self.df_flights[['departure_airport', 'arrival_airport', 'preco', 'departure_scheduled', 'arrival_scheduled']]
            print("Processed Flights Data:")
            print(processed.head())
            
            self._create_time_aware_graph()

    def _create_time_aware_graph(self):
        """Cria um grafo temporal das rotas de voo considerando conexões possíveis"""
        self.time_aware_graph = nx.DiGraph()
        
        # Primeiro, adiciona todos os voos diretos
        for _, row in self.df_flights.iterrows():
            origin_node = (row['departure_iata'], row['departure_scheduled'])
            destination_node = (row['arrival_iata'], row['arrival_scheduled'])
            self.time_aware_graph.add_edge(origin_node, destination_node, 
                                         weight=row['preco'],
                                         flight_number=row['flight_number'])
        
        # Depois, procura por conexões possíveis
        nodes = list(self.time_aware_graph.nodes())
        for node1 in nodes:
            airport1, time1 = node1
            for node2 in nodes:
                airport2, time2 = node2
                # Se os aeroportos são os mesmos e há pelo menos 1 hora de diferença
                if (airport1 == airport2 and 
                    time1 < time2 and 
                    (time2 - time1).total_seconds() >= 3600):  # 1 hora em segundos
                    # Adiciona uma aresta de conexão com peso zero
                    self.time_aware_graph.add_edge(node1, node2, 
                                                 weight=0,
                                                 is_connection=True)
        
        print("Time-aware graph created with airport-time nodes, including possible connections.")

    def plot_routes(self):
        """Plota o grafo de rotas de voo"""
        if self.time_aware_graph:
            plt.figure(figsize=(20, 10))
            pos = nx.spring_layout(self.time_aware_graph)
            nx.draw(self.time_aware_graph, pos, with_labels=False, 
                   node_size=700, node_color='skyblue', 
                   edge_color='black', width=3.0, alpha=0.5)
            edge_labels = nx.get_edge_attributes(self.time_aware_graph, 'weight')
            nx.draw_networkx_edge_labels(self.time_aware_graph, pos, 
                                       edge_labels=edge_labels, font_color='red')
            plt.title("Rotas de voo")
            plt.show()

    def extract_airport_codes(self, text):
        """Extrai códigos de aeroporto de texto usando o modelo Gemini"""
        if not self.gemini_model:
            print("Gemini model not initialized. Check your Google API key.")
            return None, None

        prompt = f"""
        Extract the start and destination airport codes from the following text.
        The airport codes are typically three-letter uppercase abbreviations.
        Return the answer in the format:
        Start: [Start Airport Code]
        Destination: [Destination Airport Code]

        Text: {text}
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text

            start_match = re.search(r"Start: ([A-Z]{3})", response_text)
            destination_match = re.search(r"Destination: ([A-Z]{3})", response_text)

            return (start_match.group(1) if start_match else None,
                    destination_match.group(1) if destination_match else None)

        except Exception as e:
            print(f"An error occurred while calling the Gemini API: {e}")
            return None, None

    def find_cheapest_path(self, start_airport_code, destination_airport_code):
        """Encontra o caminho mais barato entre dois aeroportos, considerando conexões"""
        if not self.time_aware_graph:
            print("Graph not created. Fetch flights first.")
            return None, None

        possible_start_nodes = [node for node in self.time_aware_graph.nodes() if node[0] == start_airport_code]
        possible_destination_nodes = [node for node in self.time_aware_graph.nodes() if node[0] == destination_airport_code]

        if not possible_start_nodes or not possible_destination_nodes:
            print(f"One or both airports not found: {start_airport_code} or {destination_airport_code}")
            return None, None

        min_cost = float('inf')
        best_itinerary = None

        for start_node in possible_start_nodes:
            for end_node in possible_destination_nodes:
                try:
                    current_path = dijkstra_path(self.time_aware_graph, source=start_node, target=end_node, weight='weight')
                    
                    # Calcula custo e constrói itinerário
                    current_cost = 0
                    current_itinerary = []
                    
                    for i in range(len(current_path) - 1):
                        node1 = current_path[i]
                        node2 = current_path[i + 1]
                        edge_data = self.time_aware_graph[node1][node2]
                        
                        current_cost += edge_data['weight']
                        
                        # Se não é uma conexão, é um voo
                        if not edge_data.get('is_connection', False):
                            flight_info = {
                                'from': node1[0],
                                'to': node2[0],
                                'departure': node1[1],
                                'arrival': node2[1],
                                'flight_number': edge_data.get('flight_number'),
                                'price': edge_data['weight']
                            }
                            current_itinerary.append(flight_info)
                        else:
                            # É uma conexão
                            layover_time = (node2[1] - node1[1]).total_seconds() / 3600  # em horas
                            current_itinerary.append({
                                'connection': True,
                                'airport': node1[0],
                                'duration': f"{layover_time:.1f} horas"
                            })

                    if current_cost < min_cost:
                        min_cost = current_cost
                        best_itinerary = current_itinerary

                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        return best_itinerary, min_cost