# Congress.Dev Backend
This contains the two components of the backend
- API
- Legislation Parser

## API
The API is an OpenAPI based system for interacting with the Postgres database


## Legislation Parser
The parser reads the XML from various .gov sites and creates a representation of the USCode in the database, which it then uses to reference when parsing the legislation with regex.