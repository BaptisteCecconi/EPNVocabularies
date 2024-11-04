from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace, SKOS, OWL, DCTERMS, BNode
from rdflib.collection import Collection

UCD_FILE = "src/ucd-list.txt"

with open(UCD_FILE, "r") as ucd_input:
    ucd_data = ucd_input.readlines()
    ucd_file_tag = ucd_data.pop(0)[1:].strip()
    date_tag = ucd_file_tag[-10:]
    title_tag = ucd_file_tag[:-11]
    license_tag = ucd_data.pop(-1)[1:].strip()

    graph = Graph()
    UCD = Namespace(f'https://ivoa.net/rdf/ucd/{ucd_file_tag}/#')
    graph.bind("ucd", UCD)
    VANN = Namespace('http://purl.org/vocab/vann/')
    graph.bind("vann", VANN)

    root_uri = UCD[""]
    graph.add((root_uri, RDF.type, OWL.Ontology))
    graph.add((root_uri, DCTERMS.created, Literal(date_tag, datatype="xsd:date")))
    graph.add((root_uri, DCTERMS.contributor, Literal("Baptiste Cecconi")))
    graph.add((root_uri, DCTERMS.license, URIRef("http://creativecommons.org/publicdomain/zero/1.0/")))
    graph.add((root_uri, RDFS.label, Literal(f"UCD list {title_tag}", lang="en")))
    graph.add((root_uri, DCTERMS.title, Literal(f"UCD list {title_tag}", lang="en")))
    graph.add((root_uri, VANN.preferredNamespacePrefix, Literal("ucd")))
    graph.add((root_uri, DCTERMS.description, Literal("List of UCD terms")))

    graph.add((DCTERMS.created, RDF.type, OWL.AnnotationProperty))
    graph.add((DCTERMS.contributor, RDF.type, OWL.AnnotationProperty))
    graph.add((DCTERMS.license, RDF.type, OWL.AnnotationProperty))
    graph.add((VANN.preferredNamespacePrefix, RDF.type, OWL.AnnotationProperty))

    # Syntax codes
    S = UCD['S']
    graph.add((S, RDF.type, OWL.Class))
    graph.add((S, RDFS.label, Literal("Secondary", lang="en")))
    graph.add((S, RDFS.comment, Literal("The word cannot be used as the first word to describe a single quantity", lang="en")))

    P = UCD['P']
    graph.add((P, RDF.type, OWL.Class))
    graph.add((P, RDFS.label, Literal("Primary", lang="en")))
    graph.add((P, RDFS.comment, Literal("The word can only be used as ``primary'' or first word.", lang="en")))

    Q = UCD['Q']
    graph.add((Q, RDF.type, OWL.Class))
    graph.add((Q, RDFS.label, Literal("Primary or Secondary", lang="en")))
    graph.add((Q, RDFS.comment, Literal("The word can be used indifferently as first or secondary word.", lang="en")))
    # owl:equivalentClass [ rdf:type owl:Class ;
    #                         owl:unionOf ( ucd:P
    #                                       ucd:S
    #                                     )
    #                       ] ;
    _PorS = BNode()
    _seqPS = BNode()
    _rest1 = BNode()
    graph.add((Q, OWL.equivalentClass, _PorS))
    graph.add((_PorS, OWL.unionOf, _seqPS))
    graph.add((_seqPS, RDF.first, UCD['P']))
    graph.add((_seqPS, RDF.rest, _rest1))
    graph.add((_rest1, RDF.first, UCD['S']))
    graph.add((_rest1, RDF.rest, RDF.nil))
    graph.add((_PorS, RDF.type, OWL.Class))

    E = UCD['E']
    graph.add((E, RDFS.subClassOf, Q))
    graph.add((E, RDFS.label, Literal("Photometric Quantity", lang="en")))
    graph.add((E, RDFS.comment, Literal("A photometric quantity, and can be followed by a word describing a part of the electromagnetic spectrum", lang="en")))

    C = UCD['C']
    graph.add((C, RDFS.subClassOf, Q))
    graph.add((C, RDFS.label, Literal("Colour Index", lang="en")))
    graph.add((C, RDFS.comment, Literal("A colour index, and can be followed by two successive word describing a part of the electromagnetic spectrum", lang="en")))

    V = UCD['V']
    graph.add((V, RDFS.subClassOf, Q))
    graph.add((V, RDFS.label, Literal("Vector", lang="en")))
    graph.add((V, RDFS.comment, Literal("Such a word can be followed by another describing the axis or reference frame in which the measurement is done", lang="en")))

    for ucd_item in ucd_data:
        flag, ucd_term, ucd_definition = [item.strip() for item in ucd_item.split('|')]
        term_uri = UCD[ucd_term]
        graph.add((term_uri, RDF.type, UCD[flag]))
        graph.add((term_uri, RDFS.label, Literal(ucd_term, lang="en")))
        graph.add((term_uri, RDFS.comment, Literal(ucd_definition, lang="en")))

    graph.serialize("ucd-list.ttl")