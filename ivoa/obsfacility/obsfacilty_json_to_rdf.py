from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace, SKOS, OWL, DCTERMS, BNode
import json

OBSFACILITY_FILE = "src/obsfacilities_vocabulary.json"

def fix_id(term):
    term = term.replace('"', '')
    term = term.replace('<', '-')
    while '--' in term:
        term = term.replace('--', '-')
    return term

with open(OBSFACILITY_FILE, "r") as json_input:
    json_data = json.load(json_input)

main_namespace = "https://voparis-ns.obspm.fr/rdf/ivoa/obsfacility/"
release_date = "2024-11-04"

graph = Graph()
OBSFACILITY = Namespace(f'{main_namespace}{release_date}/#')
graph.bind("obs", OBSFACILITY)
VANN = Namespace('http://purl.org/vocab/vann/')
graph.bind("vann", VANN)

root_uri = OBSFACILITY[""]
graph.add((root_uri, RDF.type, OWL.Ontology))
graph.add((root_uri, DCTERMS.created, Literal("2023-10-31", datatype="xsd:date")))
graph.add((root_uri, DCTERMS.contributor, Literal("Baptiste Cecconi")))
graph.add((root_uri, DCTERMS.contributor, Literal("Laura Debisschop")))
graph.add((root_uri, DCTERMS.license, URIRef("http://creativecommons.org/publicdomain/zero/1.0/")))
graph.add((root_uri, RDFS.label, Literal(f"OBSFACILITY list", lang="en")))
graph.add((root_uri, DCTERMS.title, Literal(f"OBSFACILITY", lang="en")))
graph.add((root_uri, VANN.preferredNamespacePrefix, Literal("obs")))
graph.add((root_uri, VANN.preferredNamespaceUri, Literal(f"{main_namespace}#")))
graph.add((root_uri, DCTERMS.description, Literal("List of Observation Facility terms")))
graph.add((DCTERMS.created, RDF.type, OWL.AnnotationProperty))
graph.add((DCTERMS.contributor, RDF.type, OWL.AnnotationProperty))
graph.add((DCTERMS.license, RDF.type, OWL.AnnotationProperty))
graph.add((VANN.preferredNamespacePrefix, RDF.type, OWL.AnnotationProperty))

for obj in json_data:
    term_uri = OBSFACILITY[fix_id(obj["@id"])]
    label = obj["rdfs:label"]
    comment = obj["rdfs:comment"]
    alt_label = obj["skos:altLabel"]
    exact_match = obj["skos:exactMatch"]
    graph.add((term_uri, RDF.type, OWL.Class))
    graph.add((term_uri, RDFS.label, Literal(label, "en")))
    graph.add((term_uri, RDFS.comment, Literal(comment, "en")))
    for item in alt_label:
        graph.add((term_uri, SKOS.altLabel, Literal(item, "en")))
    for item in exact_match:
        if "|" in item:
            if "#" in item:
                term_uri_scheme, sub_items = item.split("#")
                term_uri_join = "#"
            elif "=" in item:
                term_uri_scheme, sub_items = item.split("=")
                term_uri_join = "="
            else:
                raise Exception(item)
            for sub_item in sub_items.split("|"):
                graph.add((term_uri, SKOS.exactMatch, URIRef(f"{term_uri_scheme}{term_uri_join}{sub_item}")))
        else:
            graph.add((term_uri, SKOS.exactMatch, URIRef(item)))

graph.serialize("obsfacility.ttl", format="turtle")
