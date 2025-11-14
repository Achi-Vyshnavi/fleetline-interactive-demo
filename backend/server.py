import json
import random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('input.json', 'r') as f:
    DATA = json.load(f)

def add_traffic_eta(deliveries):
    for d in deliveries:
        base_time = random.randint(20, 60)
        traffic_factor = random.uniform(1.0, 1.5)
        d['eta'] = round(base_time * traffic_factor)
    return deliveries

def optimize_routes(trucks, deliveries):
    n = len(deliveries)
    distance_matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            else:
                row.append(abs(deliveries[i]['lat'] - deliveries[j]['lat']) + abs(deliveries[i]['lng'] - deliveries[j]['lng']))
        distance_matrix.append(row)

    manager = pywrapcp.RoutingIndexManager(n, len(trucks), 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return int(distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    routes = {}
    if solution:
        for vehicle_id in range(len(trucks)):
            index = routing.Start(vehicle_id)
            vehicle_route = []
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                vehicle_route.append(deliveries[node])
                index = solution.Value(routing.NextVar(index))
            routes[trucks[vehicle_id]['id']] = vehicle_route
    else:
        for i, truck in enumerate(trucks):
            routes[truck['id']] = deliveries[i::len(trucks)]

    return routes

@app.get("/routes")
def get_routes():
    trucks = DATA['trucks']
    deliveries = add_traffic_eta(DATA['deliveries'])
    routes = optimize_routes(trucks, deliveries)
    return routes

@app.post("/routes")
async def recalc_routes(request: Request):
    data = await request.json()
    trucks = data['trucks']
    deliveries = data['deliveries']
    deliveries = add_traffic_eta(deliveries)
    routes = optimize_routes(trucks, deliveries)
    return routes
