from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)

# Charger les données GTFS
stops = pd.read_csv('data/urbain/stops.txt')
trips = pd.read_csv('data/urbain/trips.txt')
routes = pd.read_csv('data/urbain/routes.txt')
stop_times = pd.read_csv('data/urbain/stop_times.txt')

# URLs temps réel
TRIP_UPDATE_URL = 'https://data.montpellier3m.fr/GTFS/Urbain/TripUpdate.pbdata'
VEHICLE_POSITION_URL = 'https://data.montpellier3m.fr/GTFS/Urbain/VehiclePosition.pbdata'

def get_trip_updates():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(TRIP_UPDATE_URL)
    feed.ParseFromString(response.content)
    updates = []
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip_id = entity.trip_update.trip.trip_id
            route_id = entity.trip_update.trip.route_id
            for stop_time in entity.trip_update.stop_time_update:
                updates.append({
                    'trip_id': trip_id,
                    'route_id': route_id,
                    'stop_id': stop_time.stop_id,
                    'arrival_time': stop_time.arrival.time if stop_time.arrival else None,
                    'departure_time': stop_time.departure.time if stop_time.departure else None
                })
    return updates

def get_vehicle_positions():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(VEHICLE_POSITION_URL)
    feed.ParseFromString(response.content)
    positions = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            positions.append({
                'trip_id': entity.vehicle.trip.trip_id,
                'route_id': entity.vehicle.trip.route_id,
                'lat': entity.vehicle.position.latitude,
                'lon': entity.vehicle.position.longitude,
                'bearing': entity.vehicle.position.bearing
            })
    return positions

@app.route('/api/trip_updates/<stop_id>')
def api_trip_updates(stop_id):
    updates = get_trip_updates()
    stop_updates = [u for u in updates if u['stop_id'] == stop_id]
    for u in stop_updates:
        route_name = routes.loc[routes['route_id'] == u['route_id'], 'route_short_name']
        u['route_name'] = route_name.values[0] if not route_name.empty else u['route_id']
    return jsonify(stop_updates)

@app.route('/api/vehicle_positions')
def api_vehicle_positions():
    return jsonify(get_vehicle_positions())

@app.route('/')
def index():
    return render_template('index.html', stops=stops.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)