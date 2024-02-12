---
component-id: ontology-based-music-classification
type: Software
name: Ontology based music classification using sandra
description: Classify compositions from ChoCo by relying on a DnS ontology. Developed ontologies include roman numeral analysis and Zarlino's cadence classification.
work-package:
- WP3
pilot:
- 
project: polifonia-project
resource: https://github.com/polifonia-project/ontology-based-music-classification
release-date: 12/02/2024
release-number: v0.1
release link: 
doi: 
changelog: 
licence:
- CC-BY_v4
copyright: "Copyright (c) 2024 Ontology based music classification @ University of Bologna"
contributors:
- Nicolas Lazzari <https://github.com/n28div>
credits:
- https://github.com/n28div
bibliography:
- main-publication: 
related-components:
---

# Ontology based music classification

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10649490.svg)](https://doi.org/10.5281/zenodo.10649490)

Classify compositions from ChoCo by relying on a DnS ontology. Developed ontologies include roman numeral analysis and Zarlino's cadence classification.
Use

```
python main.py -t roman_numeral
```

to retrieve a random song from ChoCo and classify it using roman numeral analysis or 

```
python main.py -t zarlino
```

## Acknowledgements

This work was supported by the EU’s Horizon Europe research and innovation
programme within the Polifonia project (grant agreement N. 101004746).
