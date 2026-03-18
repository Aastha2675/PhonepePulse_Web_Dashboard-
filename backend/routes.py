from flask import Blueprint, request, jsonify
from backend.services import *

api_routes = Blueprint("api_routes", __name__)

@api_routes.route("/api/filters")
def get_filters():
    return jsonify(get_filter_data())

# Top 10 States Ranking
@api_routes.route("/api/top10/states")
def top_10_states():
    year = request.args.get("year", type=int)
    return jsonify(get_top_10_state(year))

# Chart Data Route
@api_routes.route("/api/transaction/category")
def txn_per_category():
    year = request.args.get("year", type=int)
    state = request.args.get("state")
    return jsonify(get_txn_per_type_in_state(year, state))

# Map Shading Route
@api_routes.route("/api/map-shading")
def map_shading_route():
    t = request.args.get("type", "transaction")
    y = int(request.args.get("year"))
    q_raw = request.args.get("quarter", "1")
    q = int(q_raw.replace("Q", ""))
    return jsonify(get_map_shading_data(t, y, q))

# Summary Routes
@api_routes.route("/insurance/summary")
def insurance_summary():
    s = request.args.get("state")
    y = int(request.args.get("year"))
    q = int(request.args.get("quarter").replace("Q", ""))
    return jsonify(get_insurance_summary(s, y, q))

@api_routes.route("/transaction/summary")
def transaction_summary():
    s = request.args.get("state")
    y = int(request.args.get("year"))
    q = int(request.args.get("quarter").replace("Q", ""))
    return jsonify(get_transaction_summary(s, y, q))