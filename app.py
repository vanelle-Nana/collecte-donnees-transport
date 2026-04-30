from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
import subprocess
from analysis import generer_analyse_interactive

app = Flask(__name__)
app.secret_key = "transport_insight_vanelle_2026"

def get_db_connection():
    conn = sqlite3.connect('transport.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    is_admin = session.get('is_admin', False)
    return render_template('logiciel.html', page='accueil', is_admin=is_admin)

@app.route('/stats')
def stats():
    is_admin = session.get('is_admin', False)
    # Le filtrage des positifs est géré à l'intérieur de generer_analyse_interactive
    _, stats_data = generer_analyse_interactive()
    return render_template('logiciel.html', page='stats', stats=stats_data, is_admin=is_admin)

@app.route('/diagramme')
def diagramme():
    is_admin = session.get('is_admin', False)
    graph_html, _ = generer_analyse_interactive()
    return render_template('logiciel.html', page='diagramme', graph_html=graph_html, is_admin=is_admin)

@app.route('/gestion')
def gestion():
    is_admin = session.get('is_admin', False)
    conn = get_db_connection()
    # FILTRE : On ne récupère que les prix positifs pour l'affichage
    trajets = conn.execute('SELECT * FROM trajets WHERE prix > 0 ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('logiciel.html', page='gestion', trajets=trajets, is_admin=is_admin)

@app.route('/ajouter', methods=['POST'])
def ajouter():
    compagnie = request.form['compagnie']
    prix = request.form.get('prix', type=int)

    # SÉCURITÉ : Bloque l'ajout si le prix est 0 ou négatif
    if prix and prix > 0:
        conn = get_db_connection()
        conn.execute('INSERT INTO trajets (compagnie, depart, prix) VALUES (?, ?, ?)', 
                     (compagnie, 'Manuel', prix))
        conn.commit()
        conn.close()
    return redirect(url_for('gestion'))

@app.route('/supprimer/<int:id>')
def supprimer(id):
    if session.get('is_admin', False):
        conn = get_db_connection()
        conn.execute('DELETE FROM trajets WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('gestion'))

@app.route('/modifier/<int:id>', methods=['POST'])
def modifier(id):
    if session.get('is_admin', False):
        nouveau_prix = request.form.get('prix', type=int)
        # SÉCURITÉ : Empêche de modifier vers un prix négatif
        if nouveau_prix and nouveau_prix > 0:
            conn = get_db_connection()
            conn.execute('UPDATE trajets SET prix = ? WHERE id = ?', (nouveau_prix, id))
            conn.commit()
            conn.close()
    return redirect(url_for('gestion'))

@app.route('/toggle_admin')
def toggle_admin():
    session['is_admin'] = not session.get('is_admin', False)
    return redirect(request.referrer or url_for('home'))

@app.route('/collecter')
def collecter():
    if not session.get('is_admin', False):
        return "Accès refusé", 403
    subprocess.run(["python3", "scraper.py"])
    return redirect(url_for('gestion'))

if __name__ == '__main__':
    app.run(debug=True)