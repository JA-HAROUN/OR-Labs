from flask import Flask, jsonify, request
from flask_cors import CORS

from Simplex import Optimization_Type, Simplex

app = Flask(__name__)
CORS(app)


def _parse_goal(goal_text: str) -> Optimization_Type:
    if not goal_text:
        return Optimization_Type.NULL

    lowered = goal_text.strip().lower()
    if lowered.startswith("max"):
        return Optimization_Type.MAXIMIZATION
    if lowered.startswith("min"):
        return Optimization_Type.MINIMIZATION

    return Optimization_Type.NULL


def _validate_variable_restrictions(restrictions):
    if not restrictions:
        return True
    return all(str(r).strip() == ">=0" for r in restrictions)


@app.route("/api/solve", methods=["POST"])
def solve_simplex():
    data = request.get_json(silent=True) or {}

    goal = _parse_goal(data.get("objectiveType"))
    if goal == Optimization_Type.NULL:
        return jsonify({"error": "Invalid objectiveType"}), 400

    if not _validate_variable_restrictions(data.get("variableRestrictions")):
        return jsonify({"error": "Only >=0 variable restrictions are supported"}), 400

    constraints = data.get("constraints", [])
    obj_coeffs = data.get("objectiveCoefficients", [])
    constraints_vars = [c.get("coefficients", []) for c in constraints]
    rhs = [c.get("rhs", 0) for c in constraints]
    operators = [c.get("type", "") for c in constraints]

    simplex = Simplex(
        goal=goal,
        obj_func_coeffs=obj_coeffs,
        constraints_vars_coeffs=constraints_vars,
        RHS=rhs,
        operators=operators,
    )

    simplex.run_program()
    return jsonify(simplex.build_response())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

