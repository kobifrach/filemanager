from flask import Blueprint, request, jsonify
from ..database import get_db_connection

addFunctions_bp = Blueprint('addFunctions', __name__)  # יצירת Blueprint

