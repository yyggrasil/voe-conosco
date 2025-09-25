import requests
from random import randint
import pandas as pd
import io
import re
import os
import networkx as nx
from networkx.algorithms.shortest_paths.weighted import dijkstra_path
import matplotlib.pyplot as plt
import google.generativeai as genai


# pega a cahve da api pelo env de ambiente
api_key = os.getenv('AviationStack_api_key')
# define o endpoint da api
url = "http://api.aviationstack.com/v1/flights"
params = {
    'access_key': api_key
    # possivel usar outros valores de parametros, mas iremos pegar o geral
}

try:
    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Load the JSON response
    data = response.json()

    # Process the flight data
    flight_list = []
    if 'data' in data and data['data']:
        for flight in data['data']:
            # extrai valores importantes
            origin_iata = flight['departure']['iata'] if flight.get('departure') else None
            origin_city = flight['departure']['airport'] if flight.get('departure') else None
            destination_iata = flight['arrival']['iata'] if flight.get('arrival') else None
            destination_city = flight['arrival']['airport'] if flight.get('arrival') else None
            departure_time = flight['departure']['scheduled'] if flight.get('departure') and flight['departure'].get('scheduled') else None
            arrival_time = flight['arrival']['scheduled'] if flight.get('arrival') and flight['arrival'].get('scheduled') else None
            airline = flight['airline']['name'] if flight.get('airline') else None
            flight_number = flight['flight']['number'] if flight.get('flight') else None

            # Note: API não fornece valores de preço.

            price = randint(0,100000)/ 100 # valor imaginario de passagens

            if origin_iata and destination_iata and departure_time and arrival_time:
                 flight_list.append({
                    'Companhia': airline,
                    'Voo': flight_number,
                    'AOrigem': origin_iata,
                    'OCidade': origin_city,
                    'ADestino': destination_iata,
                    'DCidade': destination_city,
                    'HPartida': departure_time,
                    'HChegada': arrival_time,
                    'Preco': price
                })

    # cria o pandas DataFrame
    df_flights = pd.DataFrame(flight_list)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from AviationStack API: {e}")
    print("Please ensure your API key is correct and you are subscribed to the service.")



# ----------------------------------------------------------------
#
# ----------------------------------------------------------------

df_flights['HPartida'] = pd.to_datetime(df_flights['HPartida'])
df_flights['HChegada'] = pd.to_datetime(df_flights['HChegada'])
df_processed_flights = df_flights[['AOrigem', 'ADestino', 'Preco', 'HPartida', 'HChegada']]
display(df_processed_flights.head())


# ----------------------------------------------------------------
#
# ----------------------------------------------------------------



time_aware_graph = nx.DiGraph()

for index, row in df_flights.iterrows():
    origin_node = (row['AOrigem'], row['HPartida'])
    destination_node = (row['ADestino'], row['HChegada'])
    time_aware_graph.add_edge(origin_node, destination_node, weight=row['Preco'])

print("Time-aware graph created with airport-time nodes and price weights.")




plt.figure(figsize=(20, 10))
pos = nx.spring_layout(time_aware_graph)
nx.draw(time_aware_graph, pos, with_labels=False, node_size=700, node_color='skyblue', edge_color='black', width=3.0, alpha=0.5)
edge_labels = nx.get_edge_attributes(time_aware_graph, 'weight')
nx.draw_networkx_edge_labels(time_aware_graph, pos, edge_labels=edge_labels, font_color='red')
plt.title("Rotas de voo")
plt.show()




# ----------------------------------------------------------------
#
# ----------------------------------------------------------------



# Example human-written text
# [(TAO) (NGO)
text = "Find the cheapest flight from Qingdao to Chu-Bu Centrair International (Central Japan International)."

# Get your API key from Colab secrets
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# Initialize the Gemini model
gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')

# Create a prompt for the Gemini model to extract airport codes
prompt = f"""
Extract the start and destination airport codes from the following text.
The airport codes are typically three-letter uppercase abbreviations.
Return the answer in the format:
Start: [Start Airport Code]
Destination: [Destination Airport Code]

Text: {text}
"""

try:
    # Generate content using the Gemini model
    response = gemini_model.generate_content(prompt)
    response_text = response.text

    # Extract the airport codes from the Gemini model's response
    start_match = re.search(r"Start: ([A-Z]{3})", response_text)
    destination_match = re.search(r"Destination: ([A-Z]{3})", response_text)

    start_airport_code = start_match.group(1) if start_match else None
    destination_airport_code = destination_match.group(1) if destination_match else None

    if start_airport_code and destination_airport_code:
        print(f"Start airport code: {start_airport_code}")
        print(f"Destination airport code: {destination_airport_code}")
    elif start_airport_code:
        print(f"Start airport code: {start_airport_code}")
        print("Could not identify a destination airport code.")
    else:
        print("Could not identify any airport codes in the text.")

except Exception as e:
    print(f"An error occurred while calling the Gemini API: {e}")


# ----------------------------------------------------------------
#
# ----------------------------------------------------------------

# Choose a starting airport and a destination airport for pathfinding
# Choose airports that have a path with at least one connection
start_airport_code = 'TAO'
destination_airport_code = 'NGO'

# ----------------------------------------------------------------
#
# ----------------------------------------------------------------



# Identify all possible starting nodes in the time_aware_graph that correspond to the starting airport
possible_start_nodes = [node for node in time_aware_graph.nodes() if node[0] == start_airport_code]

# Identify all possible destination nodes in the time_aware_graph that correspond to the destination airport
possible_destination_nodes = [node for node in time_aware_graph.nodes() if node[0] == destination_airport_code]

cheapest_path = None
min_cost = float('inf')

if not possible_start_nodes or not possible_destination_nodes:
    print(f"One or both of the specified airports ({start_airport_code} or {destination_airport_code}) were not found in the graph.")
else:
    # Iterate through each of the possible starting nodes
    for start_node in possible_start_nodes:
        # For each starting node, iterate through each possible destination node
        for end_node in possible_destination_nodes:
            try:
                # Find the cheapest path from the current start node to the current end node
                current_path = dijkstra_path(time_aware_graph, source=start_node, target=end_node, weight='weight')

                # Calculate the total cost of the current path
                current_cost = 0
                for i in range(len(current_path) - 1):
                    u = current_path[i]
                    v = current_path[i+1]
                    current_cost += time_aware_graph[u][v]['weight']

                # Check if this path is cheaper than the current cheapest path
                if current_cost < min_cost:
                    min_cost = current_cost
                    cheapest_path = current_path

            except nx.NetworkXNoPath:
                # No path found from this specific start node to this specific end node
                continue
            except nx.NodeNotFound:
                # This should not happen if possible_start_nodes and possible_destination_nodes are from the graph
                print("An unexpected NodeNotFound error occurred.")

    # Print the cheapest path found (sequence of airport-time nodes) and its total cost
    if cheapest_path:
        print(f"The cheapest path from {start_airport_code} to {destination_airport_code} is: {cheapest_path}")
        print(f"The total cost of this path is: {min_cost}")
    else:
        print(f"No path found from {start_airport_code} to {destination_airport_code} considering time constraints.")