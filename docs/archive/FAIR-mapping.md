# FAIR 15 Sub-Principles Mapping

## F1 - Findable
All datasets and code are assigned persistent identifiers via Zenodo DOI integration. Metadata is published in standard schema.org and Dublin Core formats.

## F2 - Accessible  
All open content is accessible via HTTPS with no authentication barriers. Metadata remains accessible even when data is embargoed.

## F3 - Interoperable
Standard formats used: GeoTIFF for raster data, CSV for tabular data, NetCDF for multi-dimensional data, JSON-LD for metadata.

## F4 - Reusable
Clear licensing via EUPL-1.2 for code and CC BY-SA 4.0 for data. Provenance is documented in all workflows.

## A1 - Accessible
Data is retrievable by identifier using standard protocols. Authentication required only for proprietary hardware documentation.

## A1.1 - Protocol
HTTP/HTTPS protocols used for all public content. API endpoints follow REST standards.

## A1.2 - Authorization
Authorization framework documented in `/docs/auth.md` for restricted data access.

## A2 - Metadata Persistence
Metadata persists beyond data lifecycle. Archived in institutional repository with 10-year retention.

## I1 - Formal Language
Data uses formal, accessible, shared, and broadly applicable languages for knowledge representation.

## I2 - Vocabularies
Standard vocabularies used: CF Conventions for climate data, Darwin Core for biodiversity data.

## I3 - References
All external data includes qualified references to source datasets and publications.

## R1 - Rich Metadata
Metadata includes detailed provenance, methodology, and processing steps.

## R1.1 - License
Explicit license information included in all dataset metadata headers.

## R1.2 - Provenance
Complete processing lineage documented from raw data to final analysis products.

## R1.3 - Standards
Community standards followed for domain-specific metadata in Earth observation and ecology.

---

## Implementation Notes

All workflows use conda environment files with pinned package versions. Data processing scripts include version control hashes for full reproducibility.
