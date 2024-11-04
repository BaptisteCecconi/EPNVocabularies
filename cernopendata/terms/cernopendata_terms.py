from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace, SKOS, OWL, DCTERMS
import json
import sys

FILE_JSON = "terms.json"
FILE_RDF = "terms.ttl"


def fix_term(term):
    fixed_term = ""
    for part in term.split(" "):
        fixed_term += part[0].upper() + part[1:]
    return fixed_term


def json_to_rdf(input_file=FILE_JSON, output_file=FILE_RDF):
    CODT = Namespace("https://voparis-ns.obspm.fr/rdf/cernopendata/terms#")
    CODS = Namespace("https://voparis-ns.obspm.fr/rdf/cernopendata/schema#")
    MODSCI = Namespace("https://w3id.org/skgo/modsci#")

    rdf_graph = Graph()
    rdf_graph.base = CODT
    rdf_graph.bind("codt", CODT)
    rdf_graph.bind("cods", CODS)
    rdf_graph.bind("modsci", MODSCI)

    root_uri = CODT[""]
    rdf_graph.add((root_uri, RDF.type, OWL.Ontology))
    rdf_graph.add((root_uri, DCTERMS.created, Literal("2024-05-14")))
    rdf_graph.add((root_uri, DCTERMS.contributor, Literal("Baptiste Cecconi")))
    rdf_graph.add((root_uri, DCTERMS.license, URIRef("http://creativecommons.org/publicdomain/zero/1.0/")))
    rdf_graph.add((root_uri, RDFS.label, Literal("CERN OPEN DATA Terms Glossary")))
    rdf_graph.add((root_uri, DCTERMS.title, Literal("CERN OPEN DATA Terms Glossary")))

    rdf_graph.add((DCTERMS.created, RDF.type, OWL.AnnotationProperty))
    rdf_graph.add((DCTERMS.contributor, RDF.type, OWL.AnnotationProperty))
    rdf_graph.add((DCTERMS.license, RDF.type, OWL.AnnotationProperty))

    with open(input_file) as json_file:
        data = json.load(json_file)

    for term in data:
        term_uri = CODT[fix_term(term['anchor'])]
        rdf_graph.add((term_uri, RDF.type, OWL.Class))
        rdf_graph.add((term_uri, RDFS.label, Literal(term['anchor'], lang="en")))
        rdf_graph.add((term_uri, RDFS.comment, Literal(term['definition'], lang="en")))
        rdf_graph.add((term_uri, CODS.category, CODS[fix_term(term['category'])]))
        rdf_graph.add((term_uri, SKOS.prefLabel, Literal(term['anchor'], lang="en")))
        for item in term['term']:
            if item != term['anchor']:
                rdf_graph.add((term_uri, SKOS.altLabel, Literal(item, lang="en")))
        if "experiment" in term.keys():
            for item in term['experiment']:
                rdf_graph.add((term_uri, MODSCI.ScientificInstrument, CODS[item]))
        if "see_also" in term.keys():
            for item in term['see_also']:
                rdf_graph.add((term_uri, RDFS.seeAlso, CODT[fix_term(item['term'])]))
        if "links" in term.keys():
            for item in term['links']:
                rdf_graph.add((term_uri, RDFS.seeAlso, URIRef(item['url'])))

    rdf_graph.serialize(output_file)


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) >= 1:
        input_file = args[0]
    else:
        input_file = FILE_JSON

    if len(args) == 2:
        output_file = args[1]
    else:
        output_file = FILE_RDF

    json_to_rdf(input_file, output_file)