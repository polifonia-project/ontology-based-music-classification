import rdflib
import sandra
import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON
from harte.harte import Harte
from tabulate import tabulate
from collections import defaultdict, OrderedDict

TRIAD_MAP = {
  "maj": "MajorTriad",
  "min": "MinorTriad",
  "dim": "DiminishedTriad",
}

CHORD_ROLE_QUERY = """
    SELECT *
    WHERE {
      <%s> rdfs:subClassOf [ 
        owl:someValuesFrom <%s> ;
        owl:onProperty ?prop
      ]
    }
    """

class TonalityInference(object):
  def __init__(self, ontology_path: str):
    self.ontology_path = ontology_path
    self.graph = rdflib.Graph().parse(self.ontology_path)
    
    self.dc = sandra.DescriptionCollection.from_graph(self.graph)
    self.reasoner = sandra.Reasoner(self.dc)

  def preprocess_chord(self, chord: str) -> Harte:
    harte_chord = Harte(chord)
    harte_chord = Harte(harte_chord.prettify())

    # try converting the chord as triad otherwise
    # returns none if it is not possible to represent
    # it as a triad
    chord_description = None
    try:
      triad = harte_chord.as_triad()  

      root = triad.root().name. \
        replace("--", "DoubleFlat").replace("##", "DoubleSharp"). \
        replace("-", "Flat").replace("#", "Sharp")

      if triad.get_shorthand() in TRIAD_MAP:
        shorthand = TRIAD_MAP[triad.get_shorthand()]
        chord_description = self.dc[f"https://w3id.org/geometryofmeaning/roman-numeral-analysis/{root}{shorthand}"]
    except:
      pass
      
    return chord_description

  def infer(self, chords: list[str]) -> dict[str, tuple[float, list[str]]]:
    role_chord_map = defaultdict(list)
    for chord in chords:
      chord_role = self.preprocess_chord(chord)
      if chord_role is not None:
        role_chord_map[chord_role].append(chord)

    situation = sandra.Situation(list(role_chord_map.keys()))
    situation_enc = self.reasoner.encode(situation)

    # deduce the descriptions satisfied by the situation
    sat = self.reasoner(situation_enc)[0]

    inferred_descriptions = OrderedDict()  
    for idx in np.argsort(-sat):
      if sat[idx] > 0:
        description = self.reasoner.ontology.descriptions[idx]
        description_p = sat[idx]

        allocated_roles = []
        for role in situation.components:
          try:
            predicate = str(list(self.graph.query(CHORD_ROLE_QUERY % (str(description), str(role))))[0][0]).split("/")[-1]
            allocated_roles.append((role_chord_map[role], predicate))
          except:
            pass
        
        inferred_descriptions[str(description)] = (sat[idx], allocated_roles)
        
    return inferred_descriptions


class ZarlinoInference(object):
  def __init__(self, ontology_path: str):
    self.ontology_path = ontology_path
    self.graph = rdflib.Graph().parse(self.ontology_path)
    
    self.dc = sandra.DescriptionCollection.from_graph(self.graph)
    self.reasoner = sandra.Reasoner(self.dc)

  def preprocess_reference_chord(self, chord: str) -> Harte:
    harte_chord = Harte(chord)
    root = harte_chord.root().name.replace("-", "Flat")
    root_description = f"https://w3id.org/geometryofmeaning/zarlino-cadence-analysis/Reference_{root}"
    return self.dc[root_description] if root_description in self.dc else None

  def preprocess_target_chord(self, chord: str) -> Harte:
    harte_chord = Harte(chord)
    root = harte_chord.root().name.replace("-", "Flat")
    root_description = f"https://w3id.org/geometryofmeaning/zarlino-cadence-analysis/Target_{root}"
    return self.dc[root_description] if root_description in self.dc else None

  def infer(self, chords: list[str]) -> dict[str, tuple[float, list[str]]]:
    reference_chord = self.preprocess_reference_chord(chords[0])
    target_chord = self.preprocess_target_chord(chords[-1])
    
    if reference_chord is None or target_chord is None:
      # no inference possible!
      return {}
    else:
      situation = sandra.Situation([reference_chord, target_chord])
      situation_enc = self.reasoner.encode(situation)

      # deduce the descriptions satisfied by the situation
      sat = self.reasoner(situation_enc)[0]

      inferred_descriptions = OrderedDict()  
      for idx in np.argsort(-sat):
        if sat[idx] > 0:
          description = self.reasoner.ontology.descriptions[idx]
          description_p = sat[idx]          
          inferred_descriptions[str(description)] = (sat[idx], [])
          
      return inferred_descriptions

