from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date # Import date for default values and parsing
import json # Although jsonify is used, thinking about json might be helpful later

app = Flask(__name__)
# Ensure this path is correct and writable by the app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///InventoryAdjustment.db" # Corrected typo in filename assumption?
app.config["SECRET_KEY"] = "welcome" # Keep your secret key

db = SQLAlchemy(app)
api = Api(app)

# --- Database Model Definition ---
class InventoryAdjustment(db.Model):
    __tablename__ = 'inventory_adjustments' # Specify the table name

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    # Use date.today as default, not datetime.now which includes time
    date = db.Column(db.Date, default=date.today, nullable=False) # Date field, made nullable=False based on view logic
    reason = db.Column(db.String(100), nullable=False)  # Reason field
    description = db.Column(db.String(200), nullable=True)  # Description field
    item_name = db.Column(db.String(100), nullable=False)  # Item name field
    quantity_available = db.Column(db.Integer, nullable=False)  # Quantity available field
    new_quantity_on_hand = db.Column(db.Integer, nullable=False)  # New quantity on hand field
    quantity_adjusted = db.Column(db.Integer, nullable=False)  # Quantity adjusted field
    account = db.Column(db.String(50), nullable=False)  # Account field
    # reference_number can be nullable, remove default if not strictly needed by DB
    reference_number = db.Column(db.String(100), nullable=True)

    # Method to convert the model instance to a dictionary for JSON serialization
    def to_dict(self):
        return {
            "id": self.id,
            # Format date as ISO 8601 string
            "date": self.date.isoformat() if self.date else None,
            "reason": self.reason,
            "description": self.description,
            "item_name": self.item_name,
            "quantity_available": self.quantity_available,
            "new_quantity_on_hand": self.new_quantity_on_hand,
            "quantity_adjusted": self.quantity_adjusted,
            "account": self.account,
            "reference_number": self.reference_number
        }

    # Optional: __repr__ for easier debugging
    # def __repr__(self):
    #     return f'<InventoryAdjustment {self.id}: {self.item_name} on {self.date}>'


# --- Flask-RESTful Resource Definition ---
class InventoryAdjustmentResource(Resource):
    # GET /inventory_adjustments (all) and GET /inventory_adjustments/<int:product_id> (single)
    def get(self, product_id=None):
        if product_id:
            # Fetch a single adjustment by id
            adjustment = InventoryAdjustment.query.get(product_id)
            if adjustment:
                return jsonify(adjustment.to_dict()) # Return the dictionary using jsonify
            return {"message": "Inventory Adjustment not found"}, 404 # Standard 'message' key

        else:
            # Fetch all adjustments
            adjustments = InventoryAdjustment.query.all()
            # Return a list of dictionaries using jsonify
            return jsonify([item.to_dict() for item in adjustments])

    # POST /inventory_adjustments (create new)
    def post(self):
        # Get JSON data from the request body
        data = request.get_json()

        # --- Input Validation ---
        # Define required fields
        required_fields = ['date', 'reason', 'item_name', 'quantity_available',
                           'new_quantity_on_hand', 'quantity_adjusted', 'account']

        # Check if all required fields are present and not None/empty string (basic check)
        if not all(data.get(field) for field in required_fields):
             return {"message": "Missing one or more required fields"}, 400 # Bad Request

        # Parse and validate date
        try:
            # Expecting date in 'YYYY-MM-DD' format from the client (views.py)
            adjustment_date_str = data['date']
            adjustment_date = datetime.strptime(adjustment_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
             return {"message": "Invalid date format. Please provide date in YYYY-MM-DD format."}, 400

        # Validate quantity fields are integers
        try:
            quantity_available = int(data['quantity_available'])
            new_quantity_on_hand = int(data['new_quantity_on_hand'])
            quantity_adjusted = int(data['quantity_adjusted'])
        except (ValueError, TypeError):
             return {"message": "Invalid quantity format. Quantity fields must be integers."}, 400


        # Create a new InventoryAdjustment instance
        new_adjustment = InventoryAdjustment(
            date=adjustment_date, # Use the parsed date object
            reason=data['reason'],
            # Use .get() for optional fields, providing a default if necessary or letting it be None
            description=data.get('description'),
            item_name=data['item_name'],
            quantity_available=quantity_available, # Use validated integers
            new_quantity_on_hand=new_quantity_on_hand, # Use validated integers
            quantity_adjusted=quantity_adjusted, # Use validated integers
            account=data['account'],
            reference_number=data.get('reference_number') # Use .get()
        )

        # Add to session and commit to database
        try:
            db.session.add(new_adjustment)
            db.session.commit()
            # Return the newly created resource with 201 status code (Created)
            return jsonify(new_adjustment.to_dict()), 201
        except Exception as e:
             db.session.rollback() # Roll back the transaction on error
             # Log the error in a real application
             print(f"Database error during POST: {e}")
             return {"message": "An internal error occurred while saving the adjustment."}, 500


    # PUT /inventory_adjustments/<int:product_id> (update existing)
    def put(self, product_id):
        # 1. Fetch the adjustment to update
        # Use session.get() which is slightly preferred for fetching by primary key
        adjustment = db.session.get(InventoryAdjustment, product_id)
        if not adjustment:
            # Use a standard 'message' key for API responses
            return {"message": f"Inventory Adjustment with id {product_id} not found"}, 404 # Return 404 status code

        # 2. Get JSON data from the request body
        data = request.get_json()
        if not data: # Check if any data was sent at all
            return {"message": "No update data provided"}, 400 # Bad Request status

        # 3. Start a try block to handle potential data conversion or DB errors
        try:
            # 4. Update fields only if they are provided in the request JSON (Allow Partial Update)
            # IMPORTANT: Convert data types where necessary (date, integers)

            # Date field: Requires parsing from string
            if 'date' in data and data['date'] is not None: # Check if key exists AND value is not None
                 try:
                     # Expecting date in 'YYYY-MM-DD' format (standard from HTML date input)
                     adjustment_date_str = data['date']
                     # Ensure the string is not empty before parsing
                     if adjustment_date_str:
                         # Convert string to date object
                         adjustment.date = datetime.strptime(adjustment_date_str, '%Y-%m-%d').date()
                     else:
                         # If the client sent an empty string for a required date
                         return {"message": "Date field cannot be empty"}, 400 # Bad Request

                 except (ValueError, TypeError):
                      # Catch invalid date format errors
                      return {"message": "Invalid date format for 'date'. Please provide date in YYYY-MM-DD format."}, 400 # Bad Request

            # String fields: Update directly if present.
            # Add validation for nullable=False columns (reason, item_name, account) - check if sent data is None or empty
            if 'reason' in data:
                 # Assuming reason is required (nullable=False)
                 if data['reason'] is None or str(data['reason']).strip() == "":
                      return {"message": "Reason field cannot be empty"}, 400
                 adjustment.reason = data['reason']

            if 'description' in data: # Description is nullable=True, allow None
                # If the client sent None or empty string, assign it directly
                adjustment.description = data['description'] # Or data.get('description')

            if 'item_name' in data:
                 # Assuming item_name is required
                if data['item_name'] is None or str(data['item_name']).strip() == "":
                      return {"message": "Item Name field cannot be empty"}, 400
                adjustment.item_name = data['item_name']

            # Integer fields: Require conversion and validation
            if 'quantity_available' in data:
                 try:
                     # Check if the value is not None before converting to int
                     if data['quantity_available'] is None:
                         return {"message": "Quantity Available field cannot be null"}, 400
                     # Convert string to integer
                     adjustment.quantity_available = int(data['quantity_available'])
                 except (ValueError, TypeError):
                      # Catch errors if conversion to int fails
                      return {"message": "Invalid quantity_available format. Must be an integer."}, 400

            if 'new_quantity_on_hand' in data:
                 try:
                     if data['new_quantity_on_hand'] is None:
                          return {"message": "New Quantity on Hand field cannot be null"}, 400
                     adjustment.new_quantity_on_hand = int(data['new_quantity_on_hand'])
                 except (ValueError, TypeError):
                      return {"message": "Invalid new_quantity_on_hand format. Must be an integer."}, 400

            if 'quantity_adjusted' in data:
                 try:
                     if data['quantity_adjusted'] is None:
                         return {"message": "Quantity Adjusted field cannot be null"}, 400
                     adjustment.quantity_adjusted = int(data['quantity_adjusted'])
                 except (ValueError, TypeError):
                      return {"message": "Invalid quantity_adjusted format. Must be an integer."}, 400

            if 'account' in data:
                 # Assuming account is required
                if data['account'] is None or str(data['account']).strip() == "":
                      return {"message": "Account field cannot be empty"}, 400
                adjustment.account = data['account']

            # Reference number is nullable=True, allow None
            if 'reference_number' in data:
                 adjustment.reference_number = data['reference_number'] # Or data.get('reference_number')


            # 5. Commit changes to database
            # No need for db.session.add(find_product) here.
            # SQLAlchemy tracks changes to objects already in the session.
            db.session.commit()

            # 6. Return success message (200 OK is the default status code for success)
            # Returning the updated resource might also be useful: return jsonify(adjustment.to_dict()), 200
            return {"message": f"Inventory Adjustment with id {product_id} updated successfully"}

        # 7. Catch any exceptions during data processing or database commit
        except Exception as e:
             db.session.rollback() # Roll back the transaction on error
             # Log the error in a real application for debugging
             print(f"Database or data processing error during PUT for id {product_id}: {e}")
             # Return a generic internal server error message and 500 status
             return {"message": "An internal error occurred while updating the adjustment."}, 500

    # DELETE /inventory_adjustments/<int:product_id> (delete existing)
    def delete(self, product_id):
        # Fetch the adjustment to delete
        adjustment = InventoryAdjustment.query.get(product_id)
        if not adjustment:
            return {"message": "Inventory Adjustment not found"}, 404

        # Delete from session and commit
        try:
            db.session.delete(adjustment)
            db.session.commit()
            # Return 200 OK or 204 No Content for successful deletion
            return {"message": "Inventory Adjustment deleted successfully"}, 200 # Or 204 for no body
        except Exception as e:
             db.session.rollback()
             print(f"Database error during DELETE: {e}")
             return {"message": "An internal error occurred while deleting the adjustment."}, 500


# --- Add Resource to API ---
# This maps the URL paths to the methods in InventoryAdjustmentResource
# - '/inventory_adjustments' -> Handles GET (all) and POST
# - '/inventory_adjustments/<int:product_id>' -> Handles GET (single), PUT, DELETE
api.add_resource(InventoryAdjustmentResource, '/inventory_adjustments', '/inventory_adjustments/<int:product_id>')

# --- Database Table Creation ---
# Create the database tables if they don't exist.
# This needs to be done within the Flask application context.
with app.app_context():
    db.create_all()
    print("Database tables created or already exist.") # Optional confirmation message


# --- Running the App ---
if __name__ == '__main__':
    # Run the Flask development server
    # debug=True provides helpful error pages and auto-reloads on code changes
    # Choose a specific port, like 5000, so your client app knows where to connect
    app.run(debug=True, port=5000)