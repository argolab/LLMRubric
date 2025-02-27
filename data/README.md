# DATASET

This file outlines how datasets are stored. Currently 2 datasets are present:

- The original LLMRubric dataset with texts and probabilties.
- Hanna-Benchmark modified to look like a rubric.

For each dataset name, there is a folder with the below items:
- CSV for the dataset text.
- Probabilties by LLM.
- Other Files (Might be unused).

## LLM Probs Structure

```json
[
  {
    "model": "gpt-3.5-turbo-16k",
    "temperature": 0.1,
    "results": {
      "Q1": [
        4.362944045828275e-06,
        0.13126332109462005,
        0.44068987218160816,
        0.42771170850889856,
        0.00033073527082749717
      ],
      "Q2": [
        1.5431152928565274e-15,
        2.5063082145766757e-08,
        0.00033391786634058394,
        0.993074190346371,
        0.006591866724204597
      ],
      "Q3": [
        3.587769498416989e-12,
        0.000114898386465486,
        0.9768750797638661,
        0.0230100174595467,
        4.386534119232351e-09
      ],
      "Q4": [
        2.0986886145609137e-10,
        0.002207730421948435,
        0.7166837213852651,
        0.27947773503840856,
        0.0016308129445088478
      ],
      "Q5": [
        2.729131313450156e-12,
        0.001932204388632775,
        0.9453862001474832,
        0.05268151955215292,
        7.59090018924052e-08
      ],
      "Q6": [
        1.6282925596632277e-21,
        1.454142276987738e-11,
        0.9991200309133146,
        0.000879969072068125,
        7.58663620504618e-14
      ],
      "Q7": [
        0.2,
        0.2,
        0.2,
        0.2,
        0.2
      ],
      "Q0": [
        2.25234964961728e-11,
        0.00035213706713550113,
        1.1399853393229681e-05,
        0.9996356035190006,
        8.595379471042655e-07
      ]
    },
    "timestamps": {
      "Q1": "2025-02-18T13:12:04.563564",
      "Q2": "2025-02-18T13:12:05.095690",
      "Q3": "2025-02-18T13:12:05.595850",
      "Q4": "2025-02-18T13:12:06.055134",
      "Q5": "2025-02-18T13:12:06.834953",
      "Q6": "2025-02-18T13:12:07.268470",
      "Q7": "2025-02-18T13:12:07.271304",
      "Q0": "2025-02-18T13:12:07.882019"
    }
  }, ...
]
```