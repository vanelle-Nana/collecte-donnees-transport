import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import io
import base64
import numpy as np
from sklearn.linear_model import LinearRegression

def generer_analyse_interactive():
    try:
        conn = sqlite3.connect('transport.db')
        # On filtre ici pour ne JAMAIS avoir de données négatives
        df = pd.read_sql_query("SELECT * FROM trajets WHERE prix > 0", conn)
        conn.close()

        if df.empty:
            return None, {'moyenne': 0, 'ecart_type': 0, 'effectif': 0, 'variance': 0, 'mode': 0}

        # --- CALCULS STATISTIQUES ---
        stats = {
            'effectif': len(df),
            'moyenne': round(df['prix'].mean(), 2),
            'variance': round(df['prix'].var() if len(df) > 1 else 0, 2),
            'ecart_type': round(df['prix'].std() if len(df) > 1 else 0, 2),
            'mode': float(df['prix'].mode()[0]) if not df['prix'].mode().empty else 0
        }

        # --- GRAPHIQUES ---
        fig, axs = plt.subplots(3, 2, figsize=(14, 18))
        plt.subplots_adjust(hspace=0.4, wspace=0.3)

        # 1. Bâtons
        axs[0, 0].bar(df.index, df['prix'], color='#3498db')
        axs[0, 0].set_title("Diagramme en Bâtons")

        # 2. Bandes (Histogramme)
        axs[0, 1].hist(df['prix'], bins=8, color='#e67e22', edgecolor='white')
        axs[0, 1].set_title("Histogramme (Répartition des prix)")

        # 3. Circulaire
        rep = df['compagnie'].value_counts()
        axs[1, 0].pie(rep, labels=rep.index, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
        axs[1, 0].set_title("Diagramme Circulaire")

        # 4. Semi-Circulaire
        axs[1, 1].pie(rep, labels=rep.index, autopct='%1.1f%%', startangle=180)
        axs[1, 1].set_title("Répartition Semi-Circulaire")

        # 5. Régression
        X = np.array(df.index).reshape(-1, 1)
        y = df['prix'].values
        model = LinearRegression().fit(X, y)
        axs[2, 0].scatter(X, y, color='gray', alpha=0.5)
        axs[2, 0].plot(X, model.predict(X), color='red', linewidth=2)
        axs[2, 0].set_title("Droite de Régression")

        axs[2, 1].axis('off')

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return plot_url, stats
    except Exception as e:
        return None, {'moyenne': 0, 'ecart_type': 0, 'effectif': 0, 'variance': 0, 'mode': 0}