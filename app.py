import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Crypto Sentinel", page_icon="🦈")

API_KEY = "ZDPX5WZACTAX4JUVN84NHVR3PDKPKU7R67"
ADRESSE_CIBLE = "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503"
WEBHOOK_URL = "https://discord.gg/mGXfxngV" # <--- COLLE TON LIEN DISCORD LÀ
SEUIL_ALERT = 50 

# --- TITRE DE LA PAGE ---
st.title("🦈 Crypto Sentinel : Binance Watcher")
st.write("Ce robot surveille la blockchain Ethereum en temps réel.")

# Zone d'état (pour afficher "En cours..." ou "Pause")
status_text = st.empty()
# Zone de log (pour afficher l'historique des actions)
log_area = st.empty()

# On utilise une liste pour garder l'historique des messages à l'écran
if 'logs' not in st.session_state:
    st.session_state['logs'] = []

def ajouter_log(message):
    # Ajoute le message en haut de la liste avec l'heure
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].insert(0, f"[{now}] {message}")
    # On garde seulement les 10 dernières lignes pour pas saturer l'écran
    st.session_state['logs'] = st.session_state['logs'][:10]
    # On affiche tout
    log_area.text("\n".join(st.session_state['logs']))

def envoyer_discord(msg):
    try:
        data = {"content": msg}
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass

# --- BOUTON DE LANCEMENT ---
if st.button('Lancer le Radar 📡'):
    ajouter_log("🟢 Démarrage du système...")
    envoyer_discord("🚀 Le Bot Cloud est activé !")
    
    # BOUCLE INFINIE
    while True:
        status_text.info("👀 Scan en cours...")
        
        try:
            url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address={ADRESSE_CIBLE}&startblock=0&endblock=99999999&page=1&offset=5&sort=desc&apikey={API_KEY}"
            reponse = requests.get(url)
            data = reponse.json()

            if data.get('message') == "OK":
                liste_tx = data['result']
                
                for tx in liste_tx:
                    montant_eth = float(tx['value']) / 10**18
                    
                    if montant_eth >= SEUIL_ALERT:
                        # Vérif temps (2 min max)
                        if (int(time.time()) - int(tx['timeStamp'])) < 180:
                            direction = "🟢 IN" if tx['to'].lower() == ADRESSE_CIBLE.lower() else "🔴 OUT"
                            valeur = montant_eth * 3300
                            
                            msg = f"🚨 **WHALE ALERT !**\nBinance : {direction}\nMontant : **{montant_eth:.2f} ETH** ({valeur:,.0f} $)"
                            
                            # On envoie l'alerte
                            ajouter_log(f"ALERTE ENVOYÉE : {montant_eth:.2f} ETH")
                            envoyer_discord(msg)
                            time.sleep(2) # Petite pause anti-spam
            
            else:
                ajouter_log("Erreur API")

        except Exception as e:
            ajouter_log(f"Bug: {e}")

        status_text.success("💤 Pause... (Prochain scan dans 60s)")
        time.sleep(60)
        # Petite astuce Streamlit pour forcer le rafraîchissement sans tout casser
        st.rerun()