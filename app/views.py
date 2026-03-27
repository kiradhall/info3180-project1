"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

import os
from uuid import uuid4

from app import app, db
from app.models import Property
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Ensure we have a place to store uploaded photos
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/properties')
def properties():
    """Render the website's properties page."""
    all_properties = Property.query.all()
    return render_template('properties.html', properties=all_properties)


@app.route('/properties/create', methods=['GET', 'POST'])
def create_property():
    """Render the create property page and handle form submissions."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        rooms = request.form.get('rooms', '').strip()
        bathrooms = request.form.get('bathrooms', '').strip()
        price = request.form.get('price', '').strip().replace(',', '')
        property_type = request.form.get('property_type', '').strip()
        location = request.form.get('location', '').strip()
        photo = request.files.get('photo')

        errors = []

        # Validation
        if not title:
            errors.append('Please provide a title for the property.')
        if not description:
            errors.append('Please provide a description.')
        if not rooms:
            errors.append('Please provide the number of rooms.')
        if not bathrooms:
            errors.append('Please provide the number of bathrooms.')
        if not price:
            errors.append('Please provide the price.')
        if not property_type:
            errors.append('Please select a property type.')
        if not location:
            errors.append('Please provide a location.')
        if not photo or photo.filename == '':
            errors.append('Please upload a photo.')
        elif not allowed_file(photo.filename):
            errors.append('Photo must be a PNG, JPG, JPEG, or GIF file.')

        try:
            rooms = int(rooms)
            if rooms < 0:
                errors.append('Rooms cannot be negative.')
        except ValueError:
            errors.append('Rooms must be a valid integer.')

        try:
            bathrooms = float(bathrooms)
            if bathrooms < 0:
                errors.append('Bathrooms cannot be negative.')
        except ValueError:
            errors.append('Bathrooms must be a valid number.')

        try:
            price = float(price)
            if price < 0:
                errors.append('Price cannot be negative.')
        except ValueError:
            errors.append('Price must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('create_property.html')

        # Save photo with unique filename
        original_filename = secure_filename(photo.filename)
        extension = os.path.splitext(original_filename)[1]
        filename = f"{uuid4().hex}{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(save_path)

        # Save property to PostgreSQL
        new_property = Property(
            title=title,
            description=description,
            rooms=rooms,
            bathrooms=bathrooms,
            price=price,
            property_type=property_type,
            location=location,
            photo=filename
        )

        db.session.add(new_property)
        db.session.commit()

        flash('Property created successfully!', 'success')
        return redirect(url_for('property', propertyid=new_property.id))

    return render_template('create_property.html')


@app.route('/property/<int:propertyid>')
def property(propertyid):
    """Render the website's property page."""
    prop = Property.query.get_or_404(propertyid)
    return render_template('property.html', property=prop)


###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
