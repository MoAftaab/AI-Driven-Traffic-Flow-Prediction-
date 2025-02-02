import argparse
from sys import prefix
from turtle import color
import webbrowser
import folium
import json
import csv
import os
import datetime

TRAFFIC_NETWORK = 'data/traffic_network2.csv'

style = lambda x: {
    'color' : x['properties']['stroke'],
    'weight' : x['properties']['stroke-width']
}

def getCoords(scat):
    file = open(TRAFFIC_NETWORK, 'r')

    for row in csv.reader(file):
        if row[0] == str(scat):
            return float(row[4]) + 0.0012469, float(row[3]) + 0.0012275

    print("unable to find SCAT location")
    return 0,0

def generateGeoJson(arr):
    data = {}
    data['type'] = 'FeatureCollection'
    data['features'] = []

    for iter, route in reversed(list(enumerate(arr))):
        weight = 5
        color = "#3484F0" if iter == 0 else "#757575"
        coords = []
        for scat in route:
            lon, lat = getCoords(scat)
            coords.append([lon, lat])
        
        feature = {}
        feature['type'] = 'Feature'

        properties = {}
        properties['stroke'] = color
        properties['stroke-width'] = weight
        feature['properties'] = properties

        geometry = {}
        geometry['type'] = 'LineString'
        geometry['coordinates'] = coords
        feature['geometry'] = geometry

        data["features"].append(feature)

    return json.dumps(data)

def drawMarkers(map, src, dest):
    src_lon, src_lat = getCoords(src)
    dest_lon, dest_lat = getCoords(dest)

    folium.Marker([src_lat, src_lon], popup=f"<strong>Start</strong> SCATS: {src}", icon=folium.Icon(color='blue', icon='circle', prefix='fa')).add_to(map)
    folium.Marker([dest_lat, dest_lon], popup=f"<strong>Finish</strong> SCATS: {dest}", icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(map)

def drawNodes(map):
    file = open(TRAFFIC_NETWORK, 'r')

    for iter, row in enumerate(csv.reader(file)):
        if iter == 0:
            continue
        lon, lat = getCoords(row[0])
        folium.Circle(
            radius=5,
            location=[lat, lon],
            popup=f"SCATS: {row[0]}",
            color="#5A5A5A",
            fill=False,
            ).add_to(map)

def drawIncidents(map, incidents):
    if not incidents:
        return

    for incident in incidents:
        lon, lat = getCoords(incident.scats_number)
        color = {
            'Accident': 'red',
            'Road Work': 'orange',
            'Road Closure': 'black'
        }.get(incident.incident_type.value, 'red')
        
        folium.Marker(
            [lat, lon],
            popup=f"<strong>{incident.incident_type.value}</strong><br>{incident.description}<br>Duration: {incident.duration.total_seconds()/3600:.1f} hours",
            icon=folium.Icon(color=color, icon='warning-sign', prefix='fa')
        ).add_to(map)

def renderMap(routes, incidents=None):
    src = routes[0][0]
    dest = routes[0][-1]

    if incidents is None:
        from data.traffic_incidents import incident_simulator
        incidents = incident_simulator.get_active_incidents(datetime.datetime.now())

    routes = generateGeoJson(routes)

    # create map
    map = folium.Map(location=[-37.831219, 145.056965], zoom_start=13, tiles="cartodbpositron", zoom_control=False,
               scrollWheelZoom=False,
               dragging=False)
    
    # plot data
    folium.GeoJson(routes, style_function=style).add_to(map)

    drawMarkers(map, src, dest)
    drawNodes(map)
    drawIncidents(map, incidents)

    # save to file
    map.save("index.html")
