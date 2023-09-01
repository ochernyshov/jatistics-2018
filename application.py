from helper.analyse import standardize, translate
from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue
import pickle
import json
import sqlite3
import operator
import jsonpickle

app = Flask(__name__)
JSGlue(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vacancy")
def vacancy():
    """Get vacancy"""
    q = request.args.get("q")
    response = []
    if not q:
        q = '%%'
    else:
        q = '%' + standardize(translate(q)).decode('utf-8') + '%'
    try:
        conn = sqlite3.connect('helper/jatistic.db')
        cursor = conn.cursor()
        length = int(cursor.execute('SELECT SUM(count) FROM history WHERE vacancy_id!=1 AND date IN (SELECT max(date) FROM history);').fetchone()[0])
        response.append(length)
        rows = cursor.execute('SELECT vacancy_id, date, name, count, requirements FROM vacancies INNER JOIN history ON history.vacancy_id=vacancies.id WHERE vacancy_id!=1 AND standardized LIKE ? AND date IN (SELECT max(date) FROM history) ORDER BY count DESC;', (q,)).fetchall()
        i = 0
        for row in rows:
            if i > 9: break
            id, d, n, c, r = row
            r = pickle.loads(r)
            dic = {}
            for k in r:
                if type(k) is not str:
                    dic[k.decode('utf-8')] = r[k]
                else:
                    dic[k] = r[k]
            r = dic
            r = json.dumps(r)
            dates = []
            buf = cursor.execute('SELECT date, count FROM history WHERE vacancy_id=?;', (id,)).fetchall()
            for date in buf:
                dd, dc = date
                dates.append([dd, dc])
            response.append([d, n, c, r, dates])
            i += 1
    except Exception as e:
        return jsonify([str(e)])
        conn.close()
    conn.close()
    return jsonify(response)


if __name__ == "__main__":
    app.run()
