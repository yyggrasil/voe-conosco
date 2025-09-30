from django.shortcuts import render
from django.utils import timezone
from .FlightSearch import FlightSearch
from .models import flights
import requests
import os
from random import randint
import pandas as pd
from datetime import datetime

def index(request):
    return render(request, 'frontend/index.html')

def search_flights(request):
    query = request.GET.get('query', '')
    
    # Inicializa o FlightSearch
    fs = FlightSearch()

    # Verifica se já existem voos no banco
    existing_flights = flights.objects.all()
    
    
    if not existing_flights.exists():
        # Se não existem voos, busca da API e salva no banco
        df_flights = fs.fetch_flights()
        if df_flights is not None and not df_flights.empty:
            # Converte o DataFrame em registros do modelo
            for _, row in df_flights.iterrows():
                flights.objects.create(
                    flight_iata=row.get('flight_iata', ''),
                    flight_icao=row.get('flight_icao', ''),
                    flight_number=row.get('flight_number', ''),

                    airline_name=row.get('airline_name', ''),
                    airline_iata=row.get('airline_iata', ''),
                    airline_icao=row.get('airline_icao', ''),

                    departure_airport=row.get('departure_airport', ''),
                    departure_iata=row.get('departure_iata', ''),
                    departure_scheduled=row.get('departure_scheduled'),

                    arrival_airport=row.get('arrival_airport', ''),
                    arrival_iata=row.get('arrival_iata', ''),
                    arrival_scheduled=row.get('arrival_scheduled'),

                    status=row.get('flight_status'),
                    preco=row.get('Preco', randint(0, 100000)/100)
                )

    # Converte os resultados para o formato do df_flights
    flights_data = []
    for flight in existing_flights:
        flights_data.append({
            'flight_iata': flight.flight_iata,
            'flight_icao': flight.flight_icao,
            'airline_name': flight.airline_name,
            'airline_iata': flight.airline_iata,
            'airline_icao': flight.airline_icao,
            'flight_number': flight.flight_number,
            'departure_airport': flight.departure_airport,
            'departure_iata': flight.departure_iata,
            'departure_scheduled': flight.departure_scheduled,
            'arrival_airport': flight.arrival_airport,
            'arrival_iata': flight.arrival_iata,
            'arrival_scheduled': flight.arrival_scheduled,
            'status': flight.status,
            'preco': flight.preco
        })
    
    # Cria um DataFrame com os dados formatados
    df_flights = pd.DataFrame(flights_data)
    
    # Configura o FlightSearch com os dados do banco
    fs.df_flights = df_flights
    fs._process_flight_data()  # Processa os dados e cria o grafo
    
    # Encontra o caminho mais barato se necessário
    path = None
    cost = None
    if query:
        # Aqui você pode usar o modelo Gemini para extrair os códigos dos aeroportos da query
        origin_code, dest_code = fs.extract_airport_codes(query)
        if origin_code and dest_code:
            path, cost = fs.find_cheapest_path(origin_code, dest_code)
            if path:
                print(f"Cheapest path found with cost: R${cost:.2f}")

    itinerary = []
    if path:
        for item in path:
            if not item.get('connection'):
                # É um voo, vamos buscar no banco de dados
                flight_obj = flights.objects.filter(
                    flight_number=item['flight_number']
                ).first()
                
                if flight_obj:
                    itinerary.append(flight_obj)

            
    
    # Passa os dados para o template
    context = {
        'itinerary': itinerary,  # Lista de voos e conexões
        'cheapest_cost': cost,   # Custo total
        'has_results': bool(path),  # Se encontrou algum caminho
        'search_query': query    # Query original
    }
    
    return render(request, 'frontend/results.html', context)