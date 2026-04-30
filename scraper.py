import requests
import sqlite3

def collecter_vols_reels():
    # On utilise l'API OpenSky (Gratuit et sans clé pour les tests)
    # Elle donne les vols actuellement dans le ciel
    url = "https://opensky-network.org/api/states/all"
    
    try:
        print("Collecte en cours sur le réseau...")
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # On ne prend que les 10 premiers pour l'exemple
        vols = data['states'][:10]
        
        conn = sqlite3.connect('transport.db')
        cursor = conn.cursor()
        
        for vol in vols:
            compagnie = vol[1] if vol[1] else "Inconnue"
            depart = vol[2] # Pays d'origine
            prix = round(vol[5] if vol[5] else 0, 2) # On utilise l'altitude comme "prix" simulé pour l'analyse
            
            cursor.execute('''
                INSERT INTO trajets (compagnie, depart, arrivee, prix, date_voyage)
                VALUES (?, ?, ?, ?, ?)
            ''', (compagnie, depart, "En vol", prix, "2026-04-28"))
            
        conn.commit()
        conn.close()
        print(f"Succès ! {len(vols)} vraies données collectées et enregistrées.")
        
    except Exception as e:
        print(f"Erreur lors de la collecte réelle : {e}")

if __name__ == "__main__":
    collecter_vols_reels()