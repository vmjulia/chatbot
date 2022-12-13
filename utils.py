
import json
import os
import pandas as pd
import numpy as np
import re
from rdflib import Namespace, URIRef
import rdflib
from graph import Graph
import pickle

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
    pd.DataFrame(df, columns=['Property', 'PropertyLabel']).to_csv("utildata2/graph_properties_expanded.csv", index=False)
    
def expand_property_labels(graph_properties, wikidata_properties=None):
    data = []
    for row in graph_properties:
        property_uri = row.p
        data.append([property_uri, graph.value(property_uri, RDFS.label)])

    return pd.DataFrame(data, columns=['Property', 'PropertyLabel'])



def all_entities(graph):
    nodes = []
    for node in graph.all_nodes():
        print(node)
        if isinstance(node, URIRef) and graph.value(node, RDFS.label):
            nodes.append((node.toPython()[len(WD):], graph.value(node, RDFS.label)))
    df = pd.DataFrame(nodes, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata2/graph_entities.csv", index=False)


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
    nodes2 = [s for s in graph.objects(None, WDT.P344) if graph.value(s, RDFS.label)]
    nodes3 = [s for s in graph.objects(None, WDT.P58) if graph.value(s, RDFS.label)]
    nodes4 = [s for s in graph.objects(None, WDT.P463) if graph.value(s, RDFS.label)]
    nodes5 = [s for s in graph.objects(None, WDT.P50) if graph.value(s, RDFS.label)]
    nodes6 = [s for s in graph.objects(None, WDT.P3300) if graph.value(s, RDFS.label)]
    nodes7 = [s for s in graph.objects(None, WDT.P1346) if graph.value(s, RDFS.label)]
    nodes8 = [s for s in graph.objects(None, WDT.P451) if graph.value(s, RDFS.label)]
    nodes9 = [s for s in graph.objects(None, WDT.P725) if graph.value(s, RDFS.label)]
    nodes10 = [s for s in graph.objects(None, WDT.P1431) if graph.value(s, RDFS.label)]
    nodes11 = [s for s in graph.objects(None, WDT.P112) if graph.value(s, RDFS.label)]
    nodes12 = [s for s in graph.objects(None, WDT.P767) if graph.value(s, RDFS.label)]
    nodes13 = [s for s in graph.objects(None, WDT.P3342) if graph.value(s, RDFS.label)]
    nodes.extend(nodes2)
    nodes.extend(nodes3)
    nodes.extend(nodes4)
    nodes.extend(nodes5)
    nodes.extend(nodes6)
    nodes.extend(nodes7)
    nodes.extend(nodes8)
    nodes.extend(nodes9)
    nodes.extend(nodes10)
    nodes.extend(nodes11)
    nodes.extend(nodes12)
    nodes.extend(nodes13)
    print("here")
    nodes = list(set(nodes))

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/people_entities.csv", index=False)


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
    
def screenwriter_entities(graph):
    entities = []
    nodes = [s for s in graph.objects(None, WDT.P58) if graph.value(s, RDFS.label)]

    for s in nodes:
        entities.append((s.toPython()[len(WD):], graph.value(s, RDFS.label)))

    df = pd.DataFrame(entities, columns=['Entity', 'EntityLabel'])
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("utildata/screenwriter_entities.csv", index=False)



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
    #graph = rdflib.Graph()
    #graph.parse('data/14_graph.nt', format='turtle')
    with open('data/graph.pkl', 'rb') as file:
            graph = pickle.load(file)
            
    director_entities(graph)
            
    exit()                    
    all_entities(graph)
    movie_entities(graph)
    director_entities(graph)
    actor_entities(graph)
    character_entities(graph)
    genre_entities(graph)
    award_entities(graph)
    map_wikidata_properties(graph)
    
    # below is code for merging the two different graphs data
    exit()
    
    
    # no new meaningful entities detected, w3 is for date or just literal for big number but we do not need it in the data, we assume that general qestions for crowdsourcing are not asked
    graph_entities = set(pd.read_csv("utildata/graph_entities.csv")["Entity"].tolist())
    res = []
    for node in graph.all_nodes():
            res.append(node)
    print(res)
    res = set([r[len("http://www.wikidata.org/entity/"):] for r in res])
    difference = res.difference(graph_entities)
    print(difference)
    
    # no new meaningful predicates detected, only two added: http://www.wikidata.org/prop/direct/P520,armament
    # http://ddis.ch/atai/indirectSubclassOf,indirect subclass of
    graph_entities = set(pd.read_csv("utildata/graph_properties_expanded.csv")["Property"].tolist())
    graph_entities2 = set(pd.read_csv("utildata2/graph_properties_expanded.csv")["Property"].tolist())
    difference = graph_entities2.difference(graph_entities)
    print(difference)
    
    graph_properties = graph.query('''
        SELECT DISTINCT ?p WHERE {
            ?s ?p ?o
        }
        ''')
    
    for row in graph_properties:
        print (row.p)
    
    