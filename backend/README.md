# Congress.Dev Backend
This contains the two components of the backend
- [API](https://api.congress.dev/ui)
- Legislation Parser

## API
The API is an OpenAPI based system for interacting with the Postgres database.


## Legislation Parser
This parser is the core of the project and covers a few different processes.

### USCode Parsing
The [USCode](https://uscode.house.gov/detailed_guide.xhtml) is a collection of all codified legislation enacted by Congress. It is available in a few formats, but the one we consume is XML, each '[Release Point](https://uscode.house.gov/download/priorreleasepoints.htm)' corresponds to the codification of one or more pieces of legislation, and is comprised of over 600MB of XML.

We convert the XML into a sort of tree structure in the database for the next step. Currently we parse each Release Point entirely, so you can expect the database to grow by 3-400 MB per month due to new RPs being published.

### Legislation Parsing
Once the USCode is parsed, we can [download](https://www.govinfo.gov/bulkdata/BILLS/116/2/hr/BILLS-116-2-hr.zip) the latest copy of legislation for both the House and the Senate. Using a collection of handwritten regex, we parse the legislation text for 'actions' that each one is proposing, and we attempt to 'apply' those actions and predict what the USCode would look like once codified. The difference between the current version and our prediction version is then displayed in the frontend to highlight changes.

Currently we download the .zip bundle for both chambers every time, but recently there have been new developments in the API, so we might be able to ask for a list of bills and download each day's new legislation after you've bootstrapped the year's previous legislation.