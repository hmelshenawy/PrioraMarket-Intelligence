Product Requirements Document (PRD)
1. Overview
Product Name

Priora Vision - Cars Market Intelligence

Version

0.1 (MVP)

Status

Draft

2. Vision

Dubizzle Market Intelligence is a data-driven platform that continuously collects, stores, and analyzes Dubai's automotive marketplace data to provide users with fast, accurate, and actionable market insights.

Instead of manually browsing hundreds of listings, users can search the market, understand pricing trends, compare vehicles, and eventually receive AI-powered market value predictions.

The platform transforms raw marketplace listings into structured market intelligence.

3. Problem Statement

The Dubai used car market contains thousands of listings with constantly changing prices.

Users currently need to:

Browse hundreds of listings
Compare prices manually
Estimate market value themselves
Determine whether a vehicle is overpriced or underpriced
Track price trends manually

There is currently no simple platform that converts marketplace data into understandable market insights.

4. Objectives

The platform aims to:

Collect marketplace listings automatically
Build a historical vehicle market database
Eliminate duplicate listings
Preserve historical price snapshots
Allow users to search the market efficiently
Generate market analytics
Build machine learning models capable of estimating listing prices
Provide AI-powered explanations based on real market data
5. Target Users

Primary users include:

Used car buyers
Used car traders
Automotive enthusiasts
Market researchers

Future users may include:

Dealerships
Fleet buyers
Insurance companies
Financial institutions
6. Scope (MVP)

The initial release supports:

Dubai marketplace
Used vehicles
New vehicles

Future releases may support additional Emirates and countries.

7. Data Source

Primary data source:

Dubizzle automotive listings

The platform database becomes the internal source of truth after ingestion.

8. Product Features
8.1 Marketplace Collection

The platform periodically collects marketplace listings.

Collected information includes (when available):

Make
Model
Year
Price
Mileage
Fuel type
Transmission
Body type
Trim
Regional specifications
Seller information
Location
Photos
Listing URL
Additional marketplace metadata
8.2 Listing Management

The platform shall:

Detect duplicate listings using listing UUID
Update existing listings
Preserve historical snapshots
Track listing activity
Detect inactive listings
8.3 Market Search

Users can search listings using filters including:

Make
Model
Year
Price
Mileage
Fuel
Body type
Transmission
Regional specifications
Seller type
Location
8.4 Market Analytics

The platform shall generate market statistics including:

Average price
Median price
Minimum price
Maximum price
Listing count
Average mileage
Dealer vs private distribution
Vehicle distribution
Price ranges
8.5 AI Market Assistant

Users may ask natural language questions such as:

What is the average price of a Mercedes C200 2020?
Is AED 130,000 a fair price?
Show similar vehicles.
Compare BMW 320i and Mercedes C200.
Which model holds its value better?

The AI assistant shall answer using platform analytics rather than generating unsupported information.

8.6 Price Prediction (Future MVP Goal)

The platform shall estimate listing prices using machine learning.

Initial prediction inputs include:

Make
Model
Year
Mileage
Fuel type
Transmission
Body type
Trim
Regional specifications

Prediction output includes:

Estimated listing price
Expected price range
Confidence score
9. Functional Requirements

The system shall:

FR-001

Collect vehicle listings from the configured marketplace.

FR-002

Store collected listings in the internal database.

FR-003

Identify duplicate listings using UUID.

FR-004

Maintain historical snapshots for every listing.

FR-005

Detect inactive listings.

FR-006

Allow users to search listings.

FR-007

Provide market statistics.

FR-008

Support AI-assisted market queries.

FR-009

Support machine learning price prediction.

10. Non-Functional Requirements

The platform should:

Support incremental data collection
Preserve historical data
Be modular and extensible
Separate scraping from analytics
Support future data sources
Support future ML models
Maintain data integrity
Be scalable for additional marketplaces
11. Out of Scope (MVP)

The MVP does not include:

Vehicle purchase
Seller communication
Account management
Marketplace posting
VIN decoding
Vehicle inspection history
Financing calculations
Insurance quotations
12. Success Criteria

The MVP is considered successful when it can:

Collect marketplace listings successfully
Maintain an accurate historical database
Eliminate duplicate listings
Provide reliable market search
Generate useful market analytics
Serve as the foundation for ML-based price prediction