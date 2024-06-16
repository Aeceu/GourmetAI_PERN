from flask import Blueprint,jsonify
from sqlalchemy import text
from database import engine

ingredient_bp = Blueprint("ingredient",__name__)

@ingredient_bp.route("/ingredients/<user_id>", methods=["GET"])
def getUserIngredients(user_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    ingredient.id as ingredient_id, ingredient.name as ingredient_name, 
                    ingredient.quantity, ingredient.user_id,
                    user.id as user_id, user.first_name, user.last_name, user.email
                FROM ingredient 
                JOIN user ON user.id = ingredient.user_id 
                WHERE user.id = :val
            """),
            {"val": user_id}
        )
        ingredients = []
        for row in result.mappings():
            json_ingredient = {
                        "id": row["ingredient_id"],
                        "name": row["ingredient_name"],
                        "quantity": row["quantity"],
                        "userId": row["user_id"],
            }
            ingredients.append(json_ingredient)
        if not ingredients:
            return jsonify({"message": "No ingredients found for this user"}), 404
        return jsonify({
                 "id": row["user_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "ingredients":ingredients
            
        }), 200

# TODO: Add user ingredient

# TODO: Delete user ingredient
