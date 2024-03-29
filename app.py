#!/usr/bin/env python3

from flask import Flask, render_template, request, abort
from os import environ, uname
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

app = Flask(import_name = 'Ruokalista', static_url_path = '/')
app.config['JSON_AS_ASCII'] = False
engine = create_engine(environ.get('DB', "sqlite+pysqlite:///ruokalista.db"), echo=True, future=True)
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS RUOKALISTA(id INTEGER PRIMARY KEY, \
    nimi VARCHAR(100) UNIQUE, hinta DECIMAL(5,2))"))

@app.get("/")
def index():
    return render_template('/index.html')

@app.get("/rs/uname")
def haeJarjestelma():
    uname1 = uname()
    return {'sysname': uname1.sysname, 'nodename': uname1.nodename, 'release': uname1.release,
        'version': uname1.version, 'machine': uname1.machine}

@app.get("/rs")
def haeRuokalista():
    with engine.connect() as conn:
        ruoat = conn.execute(text("SELECT id, nimi, hinta FROM RUOKALISTA"))
        lista = []
        for ruoka in ruoat:
            lista.append({'id': ruoka[0], 'nimi': ruoka[1], 'hinta': ruoka[2]})
        return lista

@app.post("/rs")
def lisaaRuokalaji():
    with engine.connect() as conn:
        uusiRuoka = request.get_json()
        try:
            conn.execute(text("INSERT INTO RUOKALISTA(nimi, hinta) \
            VALUES (:nimi, :hinta)"), uusiRuoka)
            conn.commit()
            return (uusiRuoka, 201)
        except IntegrityError:
            abort(403)

@app.put("/rs")
def muokkaaRuokalajia():
    with engine.connect() as conn:
        muokattuRuoka = request.get_json()
        result = conn.execute(text("UPDATE RUOKALISTA SET nimi=:nimi, hinta=:hinta WHERE id=:id"), muokattuRuoka)
        conn.commit()
        return muokattuRuoka

@app.delete("/rs/<int:id>")
def poistaRuokalaji(id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM RUOKALISTA WHERE id=:id"), {"id": id})
        conn.commit()
        return {"id": id}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port = environ.get('PORT', 5000), debug = True)
