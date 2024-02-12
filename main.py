from inference import TonalityInference, ZarlinoInference
from choco import get_random_music_entity
from tabulate import tabulate
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type", choices=["roman_numeral", "zarlino"])

if __name__ == "__main__":
  args = parser.parse_args()

  _, title, chords, key = get_random_music_entity()

  if args.type == "roman_numeral":
    i = TonalityInference("roman_numeral_ontology/ontology.ttl")
  else:
    i = ZarlinoInference("zarlino_cadence/ontology.xml")

  inference = i.infer(chords)

  print(f"Title: {title}")
  print(f"Chords: {chords}")
  
  table = []
  for role, (p, details) in inference.items():
    role_name = str(role).split("/")[-1]

    details = [
      f"{predicate}: " + ", ".join(chords)
      for chords, predicate in details
    ]

    table.append((role_name, p, "\n".join(details)))

  print(tabulate(table, headers=["Key", "Probability", "Details"], tablefmt="grid"))

