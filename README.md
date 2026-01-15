# Madagascar Geological Gisement Master Sheet Database

A web-based entry platform for managing Madagascar geological gisement data (Atlas Integrated).

## Features

- ✨ **Single Entry Form**: Add individual gisement records with all required fields
- 📊 **Bulk Import**: Upload CSV or Excel files to import multiple records at once
- 🔍 **Data Query**: Search and filter records by various criteria
- 💾 **Export**: Download all data as CSV for backup or analysis
- 🗺️ **Comprehensive Data**: Tracks location, collector, geological age, coordinates, and species

## Required Fields

- **Gisement No.** - With initials of collector as prefix (e.g., JD-001)
- **Collector** - First name or initials and surname
- **Date** - Collection date
- **Locality** - Primary location
- **Locality Details** - Additional info (e.g., distance from village)
- **Geological Age** - Age classification
- **Geological Age Subzone** - Subzone classification
- **Laborde Coordinates** - X and Y coordinates
- **Lat/Long** - Latitude (S) and Longitude (E)
- **Species Recorded** - Species found at the gisement

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RPScofield/Database.git
cd Database
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set a secure secret key for production:
```bash
export SECRET_KEY="your-secure-random-secret-key-here"
```

4. Run the application:
```bash
python app.py
```

For development with debug mode:
```bash
export FLASK_DEBUG=1
python app.py
```

5. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

### Single Entry
1. Click "Single Entry" in the navigation
2. Fill in the form with gisement details
3. Click "Add Record" to save

### Bulk Import
1. Click "Bulk Import" in the navigation
2. Prepare a CSV or Excel file with the following columns:
   - gisement_no, collector, date, locality, locality_details
   - geological_age, geological_age_subzone
   - laborde_x, laborde_y, latitude, longitude
   - species_recorded
3. Upload your file and click "Import Records"

### Query Data
1. Click "Query Data" in the navigation
2. Use search filters to find specific records
3. View results in the table below
4. Delete records if needed

### Export Data
1. Click "Export CSV" in the navigation
2. Download the CSV file containing all records

## Sample CSV Format

```csv
gisement_no,collector,date,locality,locality_details,geological_age,geological_age_subzone,laborde_x,laborde_y,latitude,longitude,species_recorded
JD-001,John Doe,2024-01-15,Ambatomainty,5km north of village,Cretaceous,Upper Cretaceous,450000,8500000,-18.9167,47.5167,Species A; Species B
JD-002,Jane Smith,2024-01-16,Antsirabe,Near river,Jurassic,Middle Jurassic,455000,8505000,-19.8667,47.0333,Species C
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (embedded database)
- **Security**: Flask-WTF with CSRF protection
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Data Processing**: Pandas (for CSV/Excel import)

## Database Schema

The application uses a single SQLite database table with the following structure:
- Primary key (id)
- All required gisement fields
- Timestamps for record creation
- Support for both required and optional fields

## API Endpoints

- `GET /` - Home page
- `GET/POST /entry` - Single entry form
- `GET/POST /bulk-import` - Bulk import interface
- `GET /query` - Query and filter records
- `GET /export` - Export all records to CSV
- `POST /delete/<id>` - Delete a specific record
- `GET /api/records` - JSON API endpoint for all records

## License

This project is open source and available for geological research purposes.
