from app import db
from flask import url_for


class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(255), nullable=False)

    @property
    def photo_url(self):
        return url_for('static', filename=f'uploads/{self.photo}')