from flask_jwt_extended import create_access_token
from flask import Blueprint,jsonify,request
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from database import engine
from sqlalchemy import text
import uuid

user_bp = Blueprint("user",__name__)
bcrypt = Bcrypt()

@user_bp.route("/user",methods=["GET"])
def getUsers():
    with engine.connect() as conn:
        result = conn.execute(text("select * from user"))
        users = []
        for user in result.all():
            json_user = {
                "id":user.id,
                "firstName":user.first_name,
                "lastName":user.last_name,
                "email":user.email
            }
            users.append(json_user)
        return jsonify(list(users)),200

@user_bp.route("/signup", methods=["POST"])
def registerUser():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not first_name or not last_name or not email or not password:
        return jsonify({"error": "You must fill up the required fields"}), 400

    try:
        with engine.connect() as conn:
            #? Check if the user already exists
            result = conn.execute(text("SELECT * FROM user WHERE email = :email"), {"email": email})
            user_exists = result.fetchone()  # Get the first result if it exists

            if user_exists:
                return jsonify({"message": "Email already registered!"}), 400

            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            # UUID as the primary id of the user
            user_id = str(uuid.uuid4())

            # Insert the new user
            query = text("""
                INSERT INTO user (id, first_name, last_name, email, password)
                VALUES (:id, :first_name, :last_name, :email, :password)
            """)
            conn.execute(query, {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": hashed_password
            })
            
            conn.commit()

            return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except IntegrityError as e:
        # ? This exception is specifically caught to handle database integrity issues, such as violating a unique constraint (e.g., trying to insert a duplicate email address into the user table).
        return jsonify({"error": "A user with this email already exists"}), 409

    except Exception as e:
        # ? This catch-all Exception block is meant to handle any other unforeseen errors that might occur during the execution of your code.
        return jsonify({"error": str(e)}), 500

@user_bp.route("/login", methods=["POST"])
def loginUser():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Please fill up the missing field!"}), 400

    try:
        with engine.connect() as conn:
            result = conn.execute(text("select * from user where email = :email"), {"email": email})
            user_exists = result.fetchone()
            if user_exists is None:
                return jsonify({"error": "Email is not registered!"}), 400

            user = {
                "id": user_exists.id,
                "firstName": user_exists.first_name,
                "lastName": user_exists.last_name,
                "email": user_exists.email,
                "password": user_exists.password
            }

            valid_password = bcrypt.check_password_hash(user["password"], password)
            if not valid_password:
                return jsonify({"error": "Password incorrect!"}), 400

            accessToken = create_access_token(identity=user["id"], additional_claims=user)

            return jsonify({
                "message":"User authenticated!",
                "accessToken":accessToken,
                "user":user
            })

    except IntegrityError as e:
        print(e)
        return jsonify({"error": "A user with this email already exists"}), 409

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
