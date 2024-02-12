from SPARQLWrapper import SPARQLWrapper, JSON
from harte.harte import Harte

RANDOM_ENTITY_QUERY = open("queries/random_music_entity.sparql").read()
ENTITY_CHORDS_QUERY = open("queries/chords_of_music_entity.sparql").read()
ENTITY_KEY_QUERY = open("queries/key_of_music_entity.sparql").read()

def get_random_music_entity():
  sparql = SPARQLWrapper("https://polifonia.disi.unibo.it/choco/sparql")
  sparql.setReturnFormat(JSON)

  sparql.setQuery(RANDOM_ENTITY_QUERY)
  result = sparql.queryAndConvert()

  entity_uri = result["results"]["bindings"][0]["entity"]["value"]
  entity_title = result["results"]["bindings"][0]["title"]["value"]

  sparql.setQuery(ENTITY_CHORDS_QUERY % entity_uri)
  entity_chords = [b["chord"]["value"] for b in sparql.queryAndConvert()["results"]["bindings"]]

  sparql.setQuery(ENTITY_KEY_QUERY % entity_uri)
  try:
    entity_key = result["results"]["bindings"][0]["key"]["value"]
  except:
    entity_key = ""
  
  return (entity_uri, entity_title, entity_chords, entity_key)