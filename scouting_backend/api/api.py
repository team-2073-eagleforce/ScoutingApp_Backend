from flask import Blueprint, request, jsonify
from retrieval.retrieval import conn, c

api_bp = Blueprint(
    'api_bp', __name__,
    template_folder='templates',
    static_folder='static'
)



@api_bp.route("/", methods=["GET"])
def index():
    comp_code = request.args.get("comp")
    res = []
    results = c.execute("SELECT * FROM scouting WHERE comp_code=:comp ORDER BY team ASC, matchnumber ASC", {"comp": comp_code}).fetchall()
    for r in results:
        res.append(list(r))
        print(type(r))
    return jsonify(res)

