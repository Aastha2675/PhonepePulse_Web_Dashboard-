""" Handles HTTP requests & responses. """
from flask import Blueprint, request, jsonify
from backend.services import (
    get_filter_data,
    get_insurance_summary,
    get_transaction_summary,
    get_top_10_state_per_type,
    get_top_10_state,
    get_txn_per_type_in_state,
    get_map_shading_data
)

# modular routing
api_routes = Blueprint("api_routes", __name__)

# get year and quarter time filters data
@api_routes.route("/api/filters", methods=["GET"])
def get_filters():
    data = get_filter_data()
    return jsonify(data)


@api_routes.route("/insurance/summary", methods=["GET"])
def insurance_summary():

    state = request.args.get("state")
    if state == "All India":
        state = "India"

    year = request.args.get("year")
    quarter = request.args.get("quarter")
    
    if quarter:
        quarter = quarter.replace("Q", "")
        quarter = int(quarter)
    else:
        quarter = None

    if not year:
        return jsonify({"error": "year is required"}), 400

    # Call service layer
    data = get_insurance_summary(
        state=state,
        year=int(year),
        quarter=int(quarter) if quarter else None
    )
    
    # Return response
    return jsonify(data)

@api_routes.route("/transaction/summary", methods=["GET"])
def transaction_summary():
    state = request.args.get("state")
    year = int(request.args.get("year"))
    quarter = int(request.args.get("quarter").replace("Q", ""))

    data = get_transaction_summary(state, year, quarter)
    return jsonify(data)

@api_routes.route("/transaction/top", methods = ["GET"])
def top_transactions():
    year = request.args.get("year")
    quarter = request.args.get("quarter") 

    if quarter:
        quarter = quarter.replace("Q", "")
        quarter = int(quarter)
    else:
        quarter = None

    if not year:
        return jsonify({"error": "year is required"}), 400
    
    # call service layer
    data = get_top_10_state_per_type(
        year=int(year),
        quarter=int(quarter) if quarter else None)
    
    # return response of api call
    return jsonify(data)


@api_routes.route("/api/top10/states", methods=["GET"])
def top_10_states():
    year = request.args.get("year", type=int)
    if not year:
        return jsonify({"has_data": False, "message": "Year is required"}), 400
        
    data = get_top_10_state(year)
    return jsonify(data)


@api_routes.route("/api/transaction/category", methods=["GET"])
def txn_per_category():
    year = request.args.get("year", type=int)
    state = request.args.get("state")

    if not year:
        return jsonify({"has_data": False, "message": "Year is required"}), 400
    
    data = get_txn_per_type_in_state(year,state)
    return jsonify(data)


@api_routes.route("/api/map-shading", methods=["GET"])
def map_shading_route():
    data_type = request.args.get("type", "transaction")
    year = request.args.get("year", type=int)
    
    # Get the raw string first (e.g., "Q3")
    quarter_raw = request.args.get("quarter") 
    
    # Strip the "Q" and convert to integer (e.g., "Q3" -> 3)
    try:
        quarter = int(quarter_raw.replace("Q", ""))
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid quarter format. Use 'Q1' or '1'"}), 400

    if not year or not quarter:
        return jsonify({"error": "Missing parameters"}), 400

    # Now call the service function
    data = get_map_shading_data(data_type, year, quarter)
    return jsonify(data)
