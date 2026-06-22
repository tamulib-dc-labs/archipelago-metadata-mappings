# Archipelago Mappings

A meta-model that tracks mappings between external systems and an Archipelago Digital Object (ADO) JSON. This allows us to understand how to map various systems to Archipelago and how to create interoperability in the form of Schema.org, Solr and Facets, IIIF Presentation, OAI-PMH, and other frameworks.

## Repository Structure

```
mappings/
  main.yml       # Canonical field definitions for all ADO fields
  avalon.yml     # Avalon Media System → Archipelago mappings (by collection)
  fedora.yml     # Fedora → Archipelago mappings (by collection)
  oaktrust.yml   # OAKTrust → Archipelago mappings
  ia-book-reader.yml  # Internet Archive Book Reader mappings
csv_validator.py # Validates Archipelago ingest CSVs against main.yml
```

## The Main Profile (`main.yml`)

`main.yml` is the canonical field registry. Each entry defines:

| Key | Description |
|-----|-------------|
| `definition` | Formal field definition |
| `label` | Human-readable display label |
| `type` | Data type (`str`, `int`, `date`, `object`, `url`, `uri`) |
| `min` / `max` | Cardinality constraints (min: 1 = required) |
| `mapping` | How the field maps to OAI-PMH (DC, QDC, MODS), IIIF Presentation, and Solr facets |
| `user info` | Guidance for metadata creators |
| `example` | Representative value(s) |

Object-type fields (e.g. `agent`, `subject_linked_data`) hold structured JSON with `value` and optionally `uri`, `role`, or `authority` keys to support linked data.

### Required Fields

Fields with `min: 1` must be present in every ADO:

- `label` — Title
- `type` — ADO worktype (e.g. `Image`, `Audio`)
- `content_type` — Nature or genre of the resource
- `rights` — Rights statement URI
- `digital_origin` — How the resource became digital
- `digital_publisher` — Entity making the digital resource available

## Source System Mappings

The collection-level mapping files (`avalon.yml`, `fedora.yml`, `oaktrust.yml`) document how source system fields translate to ADO fields, organized by collection name. These capture the messiness of real migrations: a single source field often maps to multiple ADO fields depending on its content (e.g. Avalon's `Genre` maps to both `content_type` and `genre_form`), and the same ADO field may come from different source fields across collections.

## CSV Validator

`csv_validator.py` validates Archipelago ingest CSVs against the field definitions in `main.yml`. It checks:

- Required columns are present
- No unknown columns exist
- Required values are populated in each row
- Values conform to their declared type (date format, valid URI, JSON structure, etc.)
- Single-value fields (`max: 1`) do not contain multiple values
- Object fields include all required keys (e.g. `agent` needs `value` and `role`)

### Usage

```bash
# Place CSVs to validate in ./output_csvs/, then run:
python csv_validator.py
```

Errors are printed as `File_name: <file> Row <n> - field "<field>": <message>`. Exit code 0 means no errors.

## About and Acknowledgements

While distinct, this model is heavily inspired by:

- [Allinson Flex](https://github.com/samvera-labs/allinson_flex)
- [Houndstooth](https://github.com/samvera-labs/houndstooth/)
- [Scooby Snacks](https://github.com/UCSCLibrary/ScoobySnacks)
- [Dog Biscuits](https://github.com/samvera-labs/dog_biscuits)
