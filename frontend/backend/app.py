from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///wastelens.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Waste Record Model
class WasteRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    meal = db.Column(db.String(50), nullable=False)
    prepared_quantity = db.Column(db.Float, nullable=False)
    wasted_quantity = db.Column(db.Float, nullable=False)
    cost_per_kg = db.Column(db.Float, nullable=False)


# Create database
with app.app_context():
    db.create_all()


# Home API
@app.route("/")
def home():
    return jsonify({
        "message": "WASTELENS API is running!"
    })


# Get all waste records
@app.route("/api/waste", methods=["GET"])
def get_waste():
    records = WasteRecord.query.order_by(WasteRecord.id.desc()).all()

    result = []

    for record in records:
        waste_percentage = (
            record.wasted_quantity / record.prepared_quantity
        ) * 100

        money_loss = record.wasted_quantity * record.cost_per_kg

        result.append({
            "id": record.id,
            "date": record.date,
            "food_name": record.food_name,
            "meal": record.meal,
            "prepared_quantity": record.prepared_quantity,
            "wasted_quantity": record.wasted_quantity,
            "waste_percentage": round(waste_percentage, 2),
            "cost_per_kg": record.cost_per_kg,
            "money_loss": round(money_loss, 2)
        })

    return jsonify(result)


# Add waste record
@app.route("/api/waste", methods=["POST"])
def add_waste():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    prepared = float(data["prepared_quantity"])
    wasted = float(data["wasted_quantity"])

    if wasted > prepared:
        return jsonify({
            "error": "Wasted quantity cannot be greater than prepared quantity"
        }), 400

    record = WasteRecord(
        date=data["date"],
        food_name=data["food_name"],
        meal=data["meal"],
        prepared_quantity=prepared,
        wasted_quantity=wasted,
        cost_per_kg=float(data["cost_per_kg"])
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": "Waste record added successfully!"
    }), 201


if __name__ == "__main__":
    app.run(debug=True)