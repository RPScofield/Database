from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import pandas as pd
import os
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gisement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class Gisement(db.Model):
    """Model for geological gisement records"""
    id = db.Column(db.Integer, primary_key=True)
    gisement_no = db.Column(db.String(100), unique=True, nullable=False)
    collector = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    locality = db.Column(db.String(300), nullable=False)
    locality_details = db.Column(db.Text)
    geological_age = db.Column(db.String(100))
    geological_age_subzone = db.Column(db.String(100))
    laborde_x = db.Column(db.Float)
    laborde_y = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    species_recorded = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'gisement_no': self.gisement_no,
            'collector': self.collector,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'locality': self.locality,
            'locality_details': self.locality_details,
            'geological_age': self.geological_age,
            'geological_age_subzone': self.geological_age_subzone,
            'laborde_x': self.laborde_x,
            'laborde_y': self.laborde_y,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'species_recorded': self.species_recorded,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/entry', methods=['GET', 'POST'])
def entry():
    """Single entry form"""
    if request.method == 'POST':
        try:
            # Parse date
            date_str = request.form.get('date')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            
            # Safely parse float values
            def safe_float(value):
                try:
                    return float(value) if value else None
                except (ValueError, TypeError):
                    return None
            
            # Create new gisement record
            gisement = Gisement(
                gisement_no=request.form.get('gisement_no'),
                collector=request.form.get('collector'),
                date=date_obj,
                locality=request.form.get('locality'),
                locality_details=request.form.get('locality_details'),
                geological_age=request.form.get('geological_age'),
                geological_age_subzone=request.form.get('geological_age_subzone'),
                laborde_x=safe_float(request.form.get('laborde_x')),
                laborde_y=safe_float(request.form.get('laborde_y')),
                latitude=safe_float(request.form.get('latitude')),
                longitude=safe_float(request.form.get('longitude')),
                species_recorded=request.form.get('species_recorded')
            )
            
            db.session.add(gisement)
            db.session.commit()
            flash('Gisement record added successfully!', 'success')
            return redirect(url_for('entry'))
            
        except Exception as e:
            flash(f'Error adding record: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('entry.html')


@app.route('/bulk-import', methods=['GET', 'POST'])
def bulk_import():
    """Bulk import from spreadsheet"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('bulk_import'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('bulk_import'))
        
        try:
            # Read the file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                flash('Unsupported file format. Please upload CSV or Excel file.', 'error')
                return redirect(url_for('bulk_import'))
            
            # Process each row
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Parse date
                    date_obj = None
                    if pd.notna(row.get('date')):
                        if isinstance(row['date'], str):
                            date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                        else:
                            date_obj = pd.to_datetime(row['date']).date()
                    
                    # Create gisement record
                    gisement = Gisement(
                        gisement_no=str(row.get('gisement_no', '')),
                        collector=str(row.get('collector', '')),
                        date=date_obj,
                        locality=str(row.get('locality', '')),
                        locality_details=str(row.get('locality_details', '')) if pd.notna(row.get('locality_details')) else None,
                        geological_age=str(row.get('geological_age', '')) if pd.notna(row.get('geological_age')) else None,
                        geological_age_subzone=str(row.get('geological_age_subzone', '')) if pd.notna(row.get('geological_age_subzone')) else None,
                        laborde_x=float(row.get('laborde_x')) if pd.notna(row.get('laborde_x')) else None,
                        laborde_y=float(row.get('laborde_y')) if pd.notna(row.get('laborde_y')) else None,
                        latitude=float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                        longitude=float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                        species_recorded=str(row.get('species_recorded', '')) if pd.notna(row.get('species_recorded')) else None
                    )
                    
                    db.session.add(gisement)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            # Commit all records
            db.session.commit()
            
            flash(f'Successfully imported {success_count} records.', 'success')
            if error_count > 0:
                flash(f'{error_count} records failed to import. Errors: {"; ".join(errors[:5])}', 'warning')
            
            return redirect(url_for('query'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('bulk_import'))
    
    return render_template('bulk_import.html')


@app.route('/query', methods=['GET'])
def query():
    """Query and interrogate data"""
    # Get filter parameters
    gisement_no = request.args.get('gisement_no', '')
    collector = request.args.get('collector', '')
    locality = request.args.get('locality', '')
    geological_age = request.args.get('geological_age', '')
    species = request.args.get('species', '')
    
    # Build query
    query_obj = Gisement.query
    
    if gisement_no:
        query_obj = query_obj.filter(Gisement.gisement_no.contains(gisement_no))
    if collector:
        query_obj = query_obj.filter(Gisement.collector.contains(collector))
    if locality:
        query_obj = query_obj.filter(Gisement.locality.contains(locality))
    if geological_age:
        query_obj = query_obj.filter(Gisement.geological_age.contains(geological_age))
    if species:
        query_obj = query_obj.filter(Gisement.species_recorded.contains(species))
    
    # Get results
    results = query_obj.order_by(Gisement.date.desc()).all()
    
    return render_template('query.html', 
                         results=results,
                         gisement_no=gisement_no,
                         collector=collector,
                         locality=locality,
                         geological_age=geological_age,
                         species=species)


@app.route('/api/records')
def api_records():
    """API endpoint for records"""
    records = Gisement.query.all()
    return jsonify([record.to_dict() for record in records])


@app.route('/export')
def export():
    """Export all data to CSV"""
    records = Gisement.query.all()
    
    # Create DataFrame
    data = []
    for record in records:
        data.append({
            'gisement_no': record.gisement_no,
            'collector': record.collector,
            'date': record.date.strftime('%Y-%m-%d') if record.date else '',
            'locality': record.locality,
            'locality_details': record.locality_details or '',
            'geological_age': record.geological_age or '',
            'geological_age_subzone': record.geological_age_subzone or '',
            'laborde_x': record.laborde_x or '',
            'laborde_y': record.laborde_y or '',
            'latitude': record.latitude or '',
            'longitude': record.longitude or '',
            'species_recorded': record.species_recorded or ''
        })
    
    df = pd.DataFrame(data)
    
    # Create CSV in memory
    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='gisement_export.csv'
    )


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a record"""
    try:
        record = db.session.get(Gisement, id)
        if record is None:
            flash('Record not found', 'error')
            return redirect(url_for('query'))
        
        db.session.delete(record)
        db.session.commit()
        flash('Record deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting record: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('query'))


def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()
    # Debug mode should be disabled in production
    # Set environment variable FLASK_DEBUG=1 for development
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
