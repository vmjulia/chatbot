
import json
import os
import pandas as pd
import numpy as np
import re
from rdflib import Namespace, URIRef
import rdflib
from graph import Graph

WD = Namespace('http://www.wikidata.org/entity/')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SCHEMA = Namespace('http://schema.org/')

entity_type_map = {
    'TITLE': [WD.Q11424, WD.Q24856, WD.Q5398426, WD.Q7725310, WD.Q15416],
    'DIRECTOR': [WD.Q2526255, WD.Q3455803],
    'CHARACTER': [WD.Q95074, WD.Q15773347, WD.Q15632617],
    'ACTOR': [WD.Q33999, WD.Q10800557],
    'GENRE': [WD.Q483394],
    'AWARD': [WD.Q618779]
}

entity_predicate_map = {
    'DIRECTOR': [WDT.P57],
    'CHARACTER': [WDT.P1441, WDT.P674],
    'ACTOR': [WDT.P161, WDT.P175],
    'GENRE': [WDT.P136]
}

def map_wikidata_properties(graph):

    # get all the distinct wikidata properties from the graph
    graph_properties = graph.query('''
        PREFIX ns1: <http://www.wikidata.org/prop/direct/>
        SELECT DISTINCT ?p WHERE {
            ?s ?p ?o
            FILTER( STRSTARTS(str(?p), str(ns1:)) )
        }
        ''')
    # pre-saved all the properties and their labels from wikidata
    #wikidata_properties = pd.read_csv('properties.csv')
    df = []
    for row in graph_properties:
        property_uri = row.p
        df.append([property_uri, graph.value(property_uri, RDFS.label)])
    pd.DataFrame(df, columns=['Property', 'PropertyLabel']).to_csv("utildata/graph_properties_expanded.csv", index=False)
    
def expand_property_labels(graph_properties, wikidata_properties=None):
    data = []
    for row in graph_properties:
        property_uri = row.p
        data.append([property_uri, graph.value(property_uri, RDFS.label)])

    return pd.DataFrame(data, columns=['Property', 'PropertyLabel'])



def all_entities(graph):
    nodes = []
    for node in graph.all_nodes():
        if isinstance(node, URIRef) and graph.value(node, RDFS.label):
            nodes.append((node.toPython()[len(WD):], graph.value(node, RDFS.label)))
    df = pd.DataFrame(nodes, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/graph_entities.csv", index=False)


def movie_entities(graph):
    entities = []
    nodes = [s for s in graph.subjects(WDT.P57, None) if graph.value(s, RDFS.label)]

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/movie_entities.csv", index=False)


def director_entities(graph):
    entities = []
    nodes = [s for s in graph.objects(None, WDT.P57) if graph.value(s, RDFS.label)]

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/director_entities.csv", index=False)


def actor_entities(graph):
    entities = []
    nodes = [s for s in graph.objects(None, WDT.P161) if graph.value(s, RDFS.label)]

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/actor_entities.csv", index=False)


def character_entities(graph):
    entities = []
    nodes = [s for s in graph.subjects(WDT.P175, None) if graph.value(s, RDFS.label)]
    characters = [(s, p, o) for n in nodes for t in entity_type_map['CHARACTER'] for s, p, o in
                  graph.triples((n, WDT.P31, t))]

    for s, p, o in characters:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/character_entities.csv", index=False)


def genre_entities(graph):
    entities = []
    nodes = [s for s in graph.objects(None, WDT.P136) if graph.value(s, RDFS.label)]

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/genre_entities.csv", index=False)

def award_entities(graph):
    entities = []
    nodes = [s for s in graph.subjects(None, None) if graph.value(s, RDFS.label)]
    characters = [(s, p, o) for n in nodes for t in entity_type_map['AWARD'] for s, p, o in
                  graph.triples((n, WDT.P31, t))]

    for s, p, o in characters:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/award_entities.csv", index=False)



if __name__ == '__main__':
    graph = rdflib.Graph()
    graph.parse('data/14_graph.nt', format='turtle')
    all_entities(graph)
    movie_entities(graph)
    director_entities(graph)
    actor_entities(graph)
    character_entities(graph)
    genre_entities(graph)
    award_entities(graph)
    map_wikidata_properties(graph)
    
    