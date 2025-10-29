from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import models

app = Flask(__name__)
CORS(app)

# ---------------- RBAC -----------------
def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            role = request.headers.get("Role", "").lower()
            if role not in allowed_roles:
                return jsonify({"error": f"Permission denied for role '{role}'"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ---------------- CRUD -----------------
@app.route("/metadata", methods=["POST"])
@require_role(["editor"])
def add_metadata():
    data = request.json
    try:
        models.create_metadata(
            data['name'],
            data['type'],
            data.get('pii_tags',''),
            data.get('compliance_tags',''),
            data['created_by']
        )
        return jsonify({"message": "Metadata created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metadata", methods=["GET"])
@require_role(["viewer","editor"])
def list_metadata():
    try:
        result = models.read_metadata()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metadata/<int:mid>", methods=["PUT"])
@require_role(["editor"])
def update_metadata(mid):
    data = request.json
    try:
        models.update_metadata(
            mid,
            data['name'],
            data['type'],
            data.get('pii_tags',''),
            data.get('compliance_tags','')
        )
        return jsonify({"message": "Metadata updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metadata/<int:mid>", methods=["DELETE"])
@require_role(["editor"])
def delete_metadata(mid):
    try:
        models.delete_metadata(mid)
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET"])
@require_role(["viewer","editor"])
def search():
    tag = request.args.get("tag","")
    try:
        result = models.search_metadata(tag)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Lineage Visualization -----------------
@app.route("/lineage", methods=["GET"])
@require_role(["viewer","editor"])
def lineage():
    try:
        all_metadata = models.read_metadata()
        lineage_data = []

        policies = [m for m in all_metadata if m['type'] == 'policy']
        claims = [m for m in all_metadata if m['type'] == 'claim']
        reserves = [m for m in all_metadata if m['type'] == 'reserve_model']

        for p in policies:
            children_claims = [c['id'] for c in claims if c['pii_tags'] == p['pii_tags']]
            lineage_data.append({"id": p['id'], "name": p['name'], "type": p['type'], "children": children_claims})

        for c in claims:
            children_reserve = [r['id'] for r in reserves if r['pii_tags'] == c['pii_tags']]
            lineage_data.append({"id": c['id'], "name": c['name'], "type": c['type'], "children": children_reserve})

        for r in reserves:
            lineage_data.append({"id": r['id'], "name": r['name'], "type": r['type'], "children": []})

        return jsonify(lineage_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
