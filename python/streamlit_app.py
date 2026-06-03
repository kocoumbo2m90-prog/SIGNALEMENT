"""
Streamlit Interface for Signalement
Modern web application for whistleblower reporting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import urljoin

# Page configuration
st.set_page_config(
    page_title="Signalement - Système de Signalements",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:5000"

# Custom CSS
st.markdown("""
    <style>
    .main { max-width: 1400px; margin: 0 auto; }
    .report-card {
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stat-card {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=60)
def get_reports(status=None, category=None, page=1):
    """Fetch reports from API"""
    try:
        params = {"page": page, "per_page": 100}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        
        response = requests.get(f"{API_BASE_URL}/api/reports", params=params)
        if response.status_code == 200:
            return response.json()
        return {"success": False, "reports": []}
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return {"success": False, "reports": []}

def get_single_report(report_id):
    """Fetch a single report"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports/{report_id}")
        if response.status_code == 200:
            return response.json()
        return {"success": False}
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return {"success": False}

def create_report(report_data):
    """Create a new report"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/reports",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_report(report_id, report_data):
    """Update a report"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/reports/{report_id}",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_report(report_id):
    """Delete a report"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/reports/{report_id}")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_statistics():
    """Get statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports/stats/summary")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def get_categories():
    """Get available categories"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/categories")
        if response.status_code == 200:
            data = response.json()
            return [c["value"] for c in data.get("categories", [])]
        return []
    except:
        return []

def get_severities():
    """Get severity levels"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/severities")
        if response.status_code == 200:
            data = response.json()
            return [s["value"] for s in data.get("severities", [])]
        return []
    except:
        return []

def get_statuses():
    """Get statuses"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/statuses")
        if response.status_code == 200:
            data = response.json()
            return [s["value"] for s in data.get("statuses", [])]
        return []
    except:
        return []

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def page_dashboard():
    """Dashboard page"""
    st.title("📊 Tableau de Bord")
    
    # Statistics
    stats = get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Signalements",
            stats.get("total_reports", 0),
            delta=None,
            delta_color="off"
        )
    
    with col2:
        nouveau = stats.get("by_status", {}).get("Nouveau", 0)
        st.metric(
            "Nouveau",
            nouveau,
            delta=None,
            delta_color="off"
        )
    
    with col3:
        en_cours = stats.get("by_status", {}).get("En cours", 0)
        st.metric(
            "En cours",
            en_cours,
            delta=None,
            delta_color="off"
        )
    
    with col4:
        traite = stats.get("by_status", {}).get("Traité", 0)
        st.metric(
            "Traité",
            traite,
            delta=None,
            delta_color="off"
        )
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Signalements par Statut")
        status_data = stats.get("by_status", {})
        if status_data:
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Signalements par Catégorie")
        category_data = stats.get("by_category", {})
        if category_data:
            fig = px.bar(
                x=list(category_data.keys()),
                y=list(category_data.values()),
                labels={"x": "Catégorie", "y": "Nombre"}
            )
            st.plotly_chart(fig, use_container_width=True)

def page_create_report():
    """Create report page"""
    st.title("📝 Créer un Signalement")
    
    categories = get_categories()
    severities = get_severities()
    
    with st.form("report_form"):
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Titre *", max_chars=255)
        
        with col2:
            category = st.selectbox("Catégorie *", categories)
        
        description = st.text_area("Description *", height=150)
        
        col1, col2 = st.columns(2)
        
        with col1:
            severity = st.selectbox("Sévérité *", severities)
        
        with col2:
            is_anonymous = st.checkbox("Signalement anonyme", value=True)
        
        # Reporter info (if not anonymous)
        if not is_anonymous:
            st.subheader("Informations du Signalant")
            col1, col2 = st.columns(2)
            
            with col1:
                reporter_name = st.text_input("Nom")
                reporter_email = st.text_input("Email")
            
            with col2:
                reporter_phone = st.text_input("Téléphone")
        else:
            reporter_name = None
            reporter_email = None
            reporter_phone = None
        
        # Location
        st.subheader("Localisation (Optionnel)")
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input("Latitude", value=0.0, step=0.0001)
        
        with col2:
            longitude = st.number_input("Longitude", value=0.0, step=0.0001)
        
        location_address = st.text_input("Adresse")
        
        # Submit
        submitted = st.form_submit_button("📤 Soumettre le Signalement", type="primary")
        
        if submitted:
            if not title or not description or not category or not severity:
                st.error("Veuillez remplir tous les champs obligatoires (*)!")
            else:
                report_data = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "severity": severity,
                    "is_anonymous": is_anonymous,
                }
                
                if not is_anonymous:
                    report_data.update({
                        "reporter_name": reporter_name,
                        "reporter_email": reporter_email,
                        "reporter_phone": reporter_phone,
                    })
                
                if latitude != 0.0 and longitude != 0.0:
                    report_data.update({
                        "latitude": latitude,
                        "longitude": longitude,
                        "location_address": location_address,
                    })
                
                result = create_report(report_data)
                
                if result.get("success"):
                    st.success("✓ Signalement créé avec succès!")
                    st.balloons()
                    st.session_state.refresh_reports = True
                else:
                    st.error(f"✗ Erreur: {result.get('error')}")

def page_view_reports():
    """View and manage reports page"""
    st.title("📋 Signalements")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    categories = get_categories()
    statuses = get_statuses()
    
    with col1:
        search = st.text_input("🔍 Rechercher par titre")
    
    with col2:
        filter_category = st.selectbox("Catégorie", ["Tous"] + categories)
    
    with col3:
        filter_status = st.selectbox("Statut", ["Tous"] + statuses)
    
    # Fetch reports
    result = get_reports(
        status=None if filter_status == "Tous" else filter_status,
        category=None if filter_category == "Tous" else filter_category
    )
    
    reports = result.get("reports", [])
    
    # Filter by search
    if search:
        reports = [r for r in reports if search.lower() in r["title"].lower()]
    
    if not reports:
        st.info("Aucun signalement trouvé.")
        return
    
    # Display reports
    st.subheader(f"Total: {len(reports)} signalement(s)")
    
    for report in reports:
        with st.expander(f"**{report['title']}** - {report['severity']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Description:** {report['description']}")
                st.write(f"**Catégorie:** {report['category']}")
            
            with col2:
                status_color = {
                    "Nouveau": "🔴",
                    "En cours": "🟡",
                    "Traité": "🟢",
                    "Rejeté": "⚫"
                }
                st.write(f"**Statut:** {status_color.get(report['status'], '')} {report['status']}")
            
            with col3:
                st.write(f"**Sévérité:** {report['severity']}")
            
            if report.get("location_address"):
                st.write(f"**Localisation:** {report['location_address']}")
            
            st.write(f"**Date:** {report['timestamp']}")
            
            if report.get("audio_uri"):
                st.write("🎙️ Audio disponible")
            
            if report.get("media_uri"):
                st.write(f"📸 Média disponible ({report.get('media_type', 'Inconnu')})")
            
            # Edit section
            st.divider()
            st.write("**Gestion du Signalement:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_status = st.selectbox(
                    "Changer le statut",
                    get_statuses(),
                    key=f"status_{report['id']}"
                )
                
                if new_status != report['status']:
                    if st.button("✓ Mettre à jour le statut", key=f"update_btn_{report['id']}"):
                        update_result = update_report(report['id'], {"status": new_status})
                        if update_result.get("success"):
                            st.success("Statut mis à jour!")
                            st.rerun()
            
            with col2:
                admin_notes = st.text_area(
                    "Notes administrateur",
                    value=report.get("admin_notes", ""),
                    key=f"notes_{report['id']}"
                )
                
                if st.button("💾 Sauvegarder les notes", key=f"notes_btn_{report['id']}"):
                    update_result = update_report(report['id'], {"admin_notes": admin_notes})
                    if update_result.get("success"):
                        st.success("Notes sauvegardées!")
            
            # Delete button
            if st.button("🗑️ Supprimer ce signalement", key=f"delete_{report['id']}"):
                if delete_report(report['id']).get("success"):
                    st.success("Signalement supprimé!")
                    st.rerun()

def page_statistics():
    """Statistics page"""
    st.title("📊 Statistiques Détaillées")
    
    stats = get_statistics()
    
    # Overall stats
    st.subheader("Vue d'ensemble")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total", stats.get("total_reports", 0))
    
    with col2:
        st.metric("Nouveau", stats.get("by_status", {}).get("Nouveau", 0))
    
    with col3:
        st.metric("En cours", stats.get("by_status", {}).get("En cours", 0))
    
    with col4:
        st.metric("Traité", stats.get("by_status", {}).get("Traité", 0))
    
    with col5:
        st.metric("Rejeté", stats.get("by_status", {}).get("Rejeté", 0))
    
    st.divider()
    
    # Detailed charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution par Statut")
        status_data = stats.get("by_status", {})
        if status_data:
            fig = px.bar(
                x=list(status_data.keys()),
                y=list(status_data.values()),
                color=list(status_data.keys()),
                labels={"x": "Statut", "y": "Nombre"}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribution par Catégorie")
        category_data = stats.get("by_category", {})
        if category_data:
            fig = px.pie(
                values=list(category_data.values()),
                names=list(category_data.keys())
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.divider()
    st.subheader("Détails par Catégorie et Statut")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Catégories:**")
        category_df = pd.DataFrame(
            list(stats.get("by_category", {}).items()),
            columns=["Catégorie", "Nombre"]
        )
        st.dataframe(category_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Statuts:**")
        status_df = pd.DataFrame(
            list(stats.get("by_status", {}).items()),
            columns=["Statut", "Nombre"]
        )
        st.dataframe(status_df, use_container_width=True, hide_index=True)

def page_about():
    """About page"""
    st.title("ℹ️ À Propos")
    
    st.markdown("""
    ## Signalement - Système de Gestion des Signalements
    
    **Version:** 1.0.0  
    **Interface:** Streamlit  
    **Backend:** Flask REST API  
    **Base de Données:** SQLAlchemy
    
    ### Caractéristiques
    
    ✅ **Création de Signalements**
    - Signalements anonymes ou identifiés
    - Catégorisation (Sécurité, Environnement, Corruption, etc.)
    - Niveaux de sévérité
    - Informations de localisation
    
    ✅ **Gestion des Signalements**
    - Suivi du statut
    - Notes administrateur
    - Filtrage et recherche
    - Suppression de signalements
    
    ✅ **Support Multimédia**
    - Enregistrements audio
    - Photos
    - Vidéos
    - Localisation géographique
    
    ✅ **Statistiques**
    - Tableau de bord en temps réel
    - Graphiques détaillés
    - Distribution par catégorie et statut
    
    ### Guide d'Utilisation
    
    **Pour Créer un Signalement:**
    1. Accédez à "📝 Créer un Signalement"
    2. Remplissez les informations requises
    3. Choisissez l'option anonyme ou identifiée
    4. Cliquez sur "Soumettre"
    
    **Pour Gérer les Signalements:**
    1. Accédez à "📋 Signalements"
    2. Utilisez les filtres pour trouver des signalements
    3. Cliquez sur un signalement pour voir les détails
    4. Mettez à jour le statut ou les notes
    
    **Pour Consulter les Statistiques:**
    1. Accédez à "📊 Statistiques"
    2. Consultez les graphiques et métriques
    
    ### Configuration
    
    L'application se connecte à l'API Flask sur `http://localhost:5000`
    
    Assurez-vous que le serveur backend est en cours d'exécution:
    ```bash
    python app.py
    ```
    
    ### Support Technique
    
    Pour plus d'informations, consultez les fichiers de documentation:
    - `README.md` - Documentation complète
    - `QUICK_REFERENCE.md` - Référence rapide de l'API
    - `CONVERSION_SUMMARY.md` - Résumé de la conversion
    """)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application"""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100?text=Signalement", width=200)
        st.title("Signalement")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["📊 Tableau de Bord", "📝 Créer un Signalement", "📋 Signalements", 
             "📊 Statistiques", "ℹ️ À Propos"],
            index=0
        )
        
        st.markdown("---")
        st.write("**Version:** 1.0.0")
        st.write("**Statut:** ✅ En ligne")
    
    # Route to page
    if page == "📊 Tableau de Bord":
        page_dashboard()
    elif page == "📝 Créer un Signalement":
        page_create_report()
    elif page == "📋 Signalements":
        page_view_reports()
    elif page == "📊 Statistiques":
        page_statistics()
    elif page == "ℹ️ À Propos":
        page_about()

if __name__ == "__main__":
    main()
