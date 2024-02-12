from itertools import product, pairwise
import music21
import argparse
import rdflib

argparser = argparse.ArgumentParser()
argparser.add_argument("--ontology", required=False)

NOTES = ["A", "B", "C", "D", "E", "F", "G"]
MODIFIERS = [
  ("", ""), 
  ("#", "Sharp"), 
  ("-", "Flat")]

SHORTHANDS = [
  ("MajorSeventhTetrad", "MajorTriad"),
  ("MinorSeventhTetrad", "MinorTriad"),
  ("HalfDiminishedTetrad", "DiminishedTriad"),
  ("AugmentedTriad"),
]

SCALES = [
  ("MajorScale", music21.scale.MajorScale, ("MajorTriad", "MinorTriad", "MinorTriad", "MajorTriad", "MajorTriad", "MinorTriad", "DiminishedTriad")),
  ("MinorScale", music21.scale.MinorScale, ("MinorTriad", "DiminishedTriad", "MajorTriad", "MinorTriad", "MinorTriad", "MajorTriad", "MajorTriad")),
  ("HarmonicMinorScale", music21.scale.HarmonicMinorScale, ("MinorTriad", "DiminishedTriad", "AugmentedTriad", "MinorTriad", "MajorTriad", "MajorTriad", "DiminishedTriad")),
  ("MelodicMinorScale", music21.scale.MelodicMinorScale, ("MinorTriad", "MinorTriad", "AugmentedTriad", "MajorTriad", "MajorTriad", "DiminishedTriad", "DiminishedTriad")),
]

DEGREES_PROPERTIES = [
  "hasFirstDegree", "hasSecondDegree", "hasThirdDegree", "hasFourthDegree", "hasFifthDegree", "hasSixthDegree", "hasSeventhDegree"
]


if __name__ == "__main__":
  args = argparser.parse_args()

  graph = rdflib.Graph()
  graph = graph.parse("ontology.xml", format="xml")

  # generate the chords classes
  for note, (mod_short, mod_long), shorthands in product(NOTES, MODIFIERS, SHORTHANDS):
    for parent_sh, child_sh in pairwise(shorthands):
      parent_shorthand_uri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{parent_sh}")
      parent_note_name = f"{note}{mod_long}{parent_sh}"
      parent_uri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{parent_note_name}")

      child_shorthand_uri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{child_sh}")
      child_note_name = f"{note}{mod_long}{child_sh}"
      child_uri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{child_note_name}")
      
      # add the parent to the graph
      graph.add((parent_uri, rdflib.RDF.type, rdflib.OWL.Class))
      # register the parents subclass
      graph.add((parent_uri, rdflib.RDFS.subClassOf, parent_shorthand_uri))
      # TODO: label and comment
      
      # add the child to the graph
      graph.add((child_uri, rdflib.RDF.type, rdflib.OWL.Class))
      # register the parents 
      graph.add((child_uri, rdflib.RDFS.subClassOf, parent_uri))
      graph.add((child_uri, rdflib.RDFS.subClassOf, child_shorthand_uri))
      # TODO: label and comment

  # generate the scales
  for note, (mod_short, mod_long), scale in product(NOTES, MODIFIERS, SCALES):
    scale_name, scale_fn, degrees = scale

    # make sure that the scale hierarchy exists
    # add first the general scale degree
    scale_parent = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/RomanNumeralAnalysis")
    scale_iri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{scale_name}")
    graph.add((scale_iri, rdflib.RDF.type, rdflib.OWL.Class))
    graph.add((scale_iri, rdflib.RDFS.subClassOf, scale_parent))
    # TODO: label and comment

    # update scale parent to the parent of this scale
    scale_parent = scale_iri
    note_name = f"{note}{mod_long}"
    scale_name = f"{note_name}{scale_name}"
    scale_iri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{scale_name}")

    # create the scale description
    graph.add((scale_iri, rdflib.RDF.type, rdflib.OWL.Class))
    graph.add((scale_iri, rdflib.RDFS.subClassOf, scale_parent))
    # TODO: label and comment

    scale = scale_fn(f"{note}{mod_short}")
    pitches = scale.getPitches()
    simplified_pitched = music21.analysis.enharmonics.EnharmonicSimplifier(pitches).bestPitches()
    
    for pitch, degree, prop in zip(simplified_pitched, degrees, DEGREES_PROPERTIES):
      pitch_name = pitch.name. \
        replace("--", "DoubleFlat").replace("##", "DoubleSharp"). \
        replace("-", "Flat").replace("#", "Sharp")
      chord_name = f"{pitch_name}{degree}"
      
      chord_iri = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{chord_name}")

      # create the universal restriction (blank node) on the description using the current chord
      role_prop = rdflib.URIRef(f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{prop}")
      ur = rdflib.BNode()
      graph.add((ur, rdflib.RDF.type, rdflib.OWL.Restriction))
      graph.add((ur, rdflib.OWL.onProperty, role_prop))
      graph.add((ur, rdflib.OWL.someValuesFrom, chord_iri))
      graph.add((scale_iri, rdflib.RDFS.subClassOf, ur))

  graph.serialize("ontology.ttl")    