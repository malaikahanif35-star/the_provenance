# the_provenance
End-to-end ETL + EDA pipeline for ~3,000+ artworks from the Art Institute of Chicago API. Extract → clean (pandas) → validate (Pydantic) → load (SQLite) →  analyze (SQL + matplotlib/seaborn) → serve via a Next.js gallery with filters and insights.
# The Provenance
### Exploring Art Through Data

**The Provenance** is an end-to-end data engineering and exploratory data analysis (EDA) project that transforms raw museum artwork records into clean, structured, validated, and meaningful data.

Using the public **Art Institute of Chicago API**, the project collects thousands of artwork records, processes inconsistencies, validates data quality, and stores the results in a SQLite database. The processed data is then analyzed to uncover patterns in artwork periods, materials, artists, geographical origins, and museum departments.

The project also features an interactive web application that makes the artwork collection and analytical findings accessible through visualizations, filters, and an image gallery.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Data Source](#data-source)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [ETL Pipeline](#etl-pipeline)
- [Data Validation](#data-validation)
- [Database Design](#database-design)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Web Application](#web-application)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Expected Outcomes](#expected-outcomes)

---

## Project Overview

Museums preserve vast collections of artworks, but their digital records are not always consistent or complete. Missing information, inconsistent date formats, and variations in geographical descriptions make it difficult to perform meaningful analysis directly on raw museum data.

The Provenance addresses this challenge by developing an end-to-end data pipeline that converts raw artwork records into a reliable dataset suitable for analysis and visualization.

The project follows a complete data workflow:

1. Extract artwork records from a public API.
2. Clean and transform raw data using Python.
3. Validate records and identify data quality issues.
4. Store processed records in a SQLite database.
5. Perform exploratory data analysis to discover meaningful patterns.
6. Present the collection and findings through an interactive web application.

## Problem Statement

Museum datasets often contain data quality issues that limit their analytical usefulness.

Some common challenges include:

- Missing artist names and geographical information.
- Inconsistent or incomplete artwork dates.
- Variations in how materials and mediums are recorded.
- Place-of-origin fields containing different geographical levels, such as cities, regions, and countries.
- Duplicate or invalid records.

These inconsistencies make it difficult to answer questions such as:

- Which century has the highest number of artworks?
- What materials and mediums are most commonly used?
- Which geographical origins are most frequently represented?
- How are artworks distributed across museum departments?
- What proportion of the collection has unknown artists?

The Provenance aims to address these challenges through systematic data cleaning, validation, database management, and exploratory analysis.

## Data Source

The project uses the **Art Institute of Chicago Public API**.

- **API Endpoint:** https://api.artic.edu/api/v1/artworks
- **Documentation:** https://api.artic.edu/docs/
- **Access:** Public and free
- **Authentication:** No API key required
- **Response Format:** JSON

The API provides access to a collection of approximately 133,000 artworks.

For this project, we aim to extract at least **3,000 artwork records**, using pagination to retrieve 100 records per request.

### Selected Dataset Fields

| Field | Description |
|---|---|
| `id` | Unique artwork identifier |
| `title` | Artwork title |
| `artist` | Artist or creator name |
| `date_start` | Starting year of the artwork's date range |
| `date_end` | Ending year of the artwork's date range |
| `medium` | Materials and techniques used |
| `place_of_origin` | Geographical origin of the artwork |
| `department` | Museum department |
| `classification` | Artwork classification |
| `image_id` | Identifier used to retrieve artwork images |

## Project Objectives

- Build a reproducible Python-based ETL pipeline.
- Retrieve artwork data through API pagination.
- Improve data quality through cleaning and transformation.
- Validate records using structured validation rules.
- Separate invalid records for further inspection.
- Store clean data in a SQLite relational database.
- Perform meaningful exploratory data analysis using SQL and Python.
- Identify trends and patterns within the museum collection.
- Develop an interactive web application to present the results.

## System Architecture

The project follows a modular ETL architecture:

**Extract → Transform → Validate → Load → Analyze → Visualize**

```text
        Art Institute of Chicago API
                    |
                    v
             DATA EXTRACTION
          (Python + Requests)
                    |
                    v
              Raw JSON Data
                    |
                    v
           DATA TRANSFORMATION
               (Pandas)
                    |
                    v
             DATA VALIDATION
               (Pydantic)
                    |
             +------+------+
             |             |
             v             v
        Valid Records   Rejected Records
             |
             v
          DATA LOADING
            (SQLite)
             |
        +----+-----+
        |          |
        v          v
      EDA      Clean JSON
        |          |
        v          v
   Charts &    Next.js Web App
   Insights         |
                    v
              Vercel Deployment
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Requests | API communication and data extraction |
| Pandas | Data cleaning and transformation |
| Pydantic | Data validation and schema enforcement |
| SQLite | Relational database storage |
| SQL | Data querying and analysis |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualizations |
| Next.js | Frontend web application |
| Vercel | Web application deployment |
| Git & GitHub | Version control and collaboration |

## ETL Pipeline

### 1. Extraction

Artwork records are retrieved from the Art Institute of Chicago API using Python's `requests` library.

The extraction process includes:

- API pagination to retrieve records in batches of 100.
- Selection of relevant artwork fields.
- HTTP error handling and request validation.
- Storage of raw API responses as JSON backups.
- Collection of at least 3,000 artwork records.

### 2. Transformation

The extracted records are processed using Pandas to improve consistency and prepare the dataset for analysis.

Transformation operations include:

- Removing duplicate records using artwork IDs.
- Handling missing artist information.
- Cleaning and standardizing text fields.
- Processing artwork date fields.
- Creating a derived `century` column from artwork dates.
- Preparing categorical fields for analysis.

### 3. Validation

Pydantic is used to enforce data quality rules and validate individual artwork records.

Validation rules include:

- Artwork ID must be a positive integer.
- Artwork title must not be empty.
- Ending year must not precede the starting year.
- Artwork dates must fall within the defined valid year range.
- Required fields must follow the expected data types.

Records that fail validation are separated into a rejected dataset, along with the corresponding validation error or rejection reason.

### 4. Loading

Validated records are loaded into a SQLite database named `artworks.db`.

The clean dataset is also exported to JSON to support integration with the web application.

## Database Design

The project uses SQLite as its relational database management system.

- **Database:** `artworks.db`
- **Table:** `artworks`
- **Primary Key:** `id`

The database stores the cleaned and validated artwork records.

| Column | Data Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| title | TEXT | Artwork title |
| artist | TEXT | Artist name |
| date_start | INTEGER | Starting year |
| date_end | INTEGER | Ending year |
| medium | TEXT | Artwork medium |
| place_of_origin | TEXT | Geographical origin |
| department | TEXT | Museum department |
| classification | TEXT | Artwork classification |
| image_id | TEXT | Artwork image identifier |
| century | INTEGER | Derived century value |

SQLite was selected because it provides a lightweight, serverless relational database that is easy to manage, share, and integrate with Python.

## Exploratory Data Analysis (EDA)

Exploratory Data Analysis is performed on the cleaned data retrieved from the SQLite database using SQL and Python.

The analysis focuses on understanding the composition, historical distribution, and characteristics of the museum's artwork collection.

### Planned Analysis

**1. Summary Statistics**
- Total number of artworks.
- Earliest and latest artwork dates.
- Overview of numerical and categorical fields.

**2. Missing Value Analysis**
- Missing artist names.
- Missing dates.
- Missing mediums and geographical origins.
- Overall data completeness.

**3. Artwork Year Distribution**
- Distribution of artworks across historical periods.
- Identification of periods with the highest representation.

**4. Artworks per Century**
- Number of artworks associated with each century.
- Identification of the most represented century.

**5. Most Common Mediums**
- Ranking of frequently used materials and techniques.

**6. Top Places of Origin**
- Geographical distribution of artworks.
- Identification of the most frequently recorded origins.

**7. Department Distribution**
- Number of artworks belonging to each museum department.

**8. Unknown Artist Analysis**
- Percentage of artworks with missing or unknown artist information.

### Visualizations

The analysis will be presented through charts and graphs using Matplotlib and Seaborn.

The final EDA will include approximately 4–6 key written insights explaining the most significant patterns discovered in the dataset.

## Web Application

The Provenance will include an interactive web application developed using Next.js and deployed through Vercel.

The application will transform the processed dataset and analytical findings into an accessible visual experience.

### Planned Features

**1. Artwork Gallery**
- Browse artwork images and titles.
- Display artist names, dates, mediums, and origins.
- Retrieve images using the Art Institute of Chicago image IDs.

**2. Interactive Filters**
- Filter artworks by century.
- Filter by artist.
- Filter by medium.
- Filter by department.
- Filter by geographical origin.

**3. Insights Dashboard**
- Display EDA visualizations.
- Highlight the most represented centuries.
- Present popular mediums and geographical origins.
- Show artwork distribution across departments.
- Display the percentage of unknown artists.

**4. Pipeline Summary**
- Total records extracted.
- Number of duplicate or invalid records rejected.
- Number of validated records loaded.
- Overview of the data processing results.

### Deployment

The frontend application will be deployed using **Vercel**.

The processed JSON dataset will serve as the data source for the web application.

## Project Structure

```text
The-Provenance/
│
├── data/
│   ├── raw/
│   │   └── artworks_raw.json
│   │
│   ├── processed/
│   │   └── artworks_clean.json
│   │
│   └── rejected/
│       └── artworks_rejected.json
│
├── database/
│   └── artworks.db
│
├── notebooks/
│   └── eda.ipynb
│
├── src/
│   ├── extraction.py
│   ├── transformation.py
│   ├── validation.py
│   ├── database.py
│   └── main.py
│
├── visualizations/
│
├── web/
│   └── nextjs-application/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

Make sure the following tools are installed:

- Python 3.11 or later
- Git
- Node.js and npm (for the web application)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd The-Provenance
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the ETL Pipeline

```bash
python src/main.py
```

This will execute the extraction, transformation, validation, and loading stages of the pipeline.

### 5. Run the Web Application

Navigate to the web application directory:

```bash
cd web/nextjs-application
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the application at:

```text
http://localhost:3000
```

*Note: These commands reflect the planned project structure and will be updated as implementation progresses.*

## Expected Outcomes

By the end of the project, The Provenance aims to deliver:

- A reusable Python ETL pipeline for extracting and processing museum artwork data.
- A cleaned and validated dataset containing at least 3,000 artwork records.
- A rejected records file documenting data quality issues.
- A structured SQLite database containing validated artwork records.
- A JSON dataset for frontend integration.
- An EDA report featuring statistical summaries, visualizations, and 4–6 key insights.
- An interactive web application showcasing the artwork collection and analytical findings.

---

## Project Vision

**Turning fragmented museum records into meaningful stories through data.**

The Provenance demonstrates how data engineering and exploratory data analysis can transform inconsistent real-world datasets into structured, reliable, and accessible information.

By combining API integration, data cleaning, validation, SQL, statistical analysis, and web development, the project connects the technical process of data engineering with the discovery and visualization of cultural heritage.

---

*Built as a collaborative data engineering and analytics project.*
