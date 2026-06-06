import os
import logging
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from models import db
from config import config
from routes.reports import api_bp
from routes.media import media_bp
from utils.excel_helper import ExcelHelper

# Configuration du logging globale
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Crée et configure l'application Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    basedir = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    # Chargement de la configuration
    app.config.from_object(config[config_name])
    
    # Création des dossiers de téléchargement
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['AUDIO_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['MEDIA_FOLDER']).mkdir(parents=True, exist_ok=True)
    
    # Initialisation des extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Enregistrement des blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(media_bp)

    # Route pour permettre à l'interface d'accéder aux fichiers médias stockés localement
    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        return send_from_directory(app.config['MEDIA_FOLDER'], filename)
        
    # ==================== Gestion des Erreurs ====================
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Une erreur inattendue est survenue.")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    # ==================== Routes Basiques ====================
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'status': 'API is running',
            'version': '1.0.0'
        }), 200
    
    @app.route('/', methods=['GET'])
    def index():
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerte Citoyenne</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0B0E14; color: #E2E8F0; font-family: 'Segoe UI', system-ui, sans-serif; }
        .card-dark { background-color: #111622; border: 1px solid #1E2640; }
        .input-dark { background-color: #0B0E14; border: 1px solid #2A3656; color: white; }
        .input-dark:focus { border-color: #3B82F6; outline: none; }
    </style>
</head>
<body class="flex justify-center items-center min-h-screen p-4">
    <div class="w-full max-w-md card-dark rounded-3xl p-6 shadow-2xl relative overflow-hidden">
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-3">
                <div class="bg-blue-600/20 p-2 rounded-xl text-blue-400">
                    <i class="fa-solid fa-shield-halved text-xl"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg leading-tight">Alerte Citoyenne</h1>
                    <p class="text-xs text-gray-400">Plateforme de signalement sécurisée</p>
                </div>
            </div>
        </div>
        <div class="bg-blue-950/40 border border-blue-900/60 rounded-2xl p-4 mb-6 flex gap-3">
            <i class="fa-solid fa-lock text-blue-400 text-lg mt-1"></i>
            <div>
                <h4 class="text-sm font-semibold text-blue-300 mb-1">Donner l'alerte de manière sécurisée</h4>
                <p class="text-xs text-blue-200/80 leading-relaxed">
                    Cette application garantit l'anonymat total. Vos fichiers sont chiffrés et l'historique est purgé.
                </p>
            </div>
        </div>
        <form id="reportForm" class="space-y-6">
            <div>
                <h3 class="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3">1. Détails du signalement</h3>
                <div class="space-y-4">
                    <input type="text" id="title" placeholder="Titre de l'alerte" class="w-full py-3 px-4 rounded-xl input-dark text-sm" required>
                    <div class="grid grid-cols-2 gap-3">
                        <select id="category" class="w-full p-3 rounded-xl input-dark text-sm">
                            <option value="Sécurité">Sécurité</option>
                            <option value="Environnement">Environnement</option>
                            <option value="Corruption">Corruption</option>
                            <option value="Santé publique">Santé publique</option>
                        </select>
                        <select id="severity" class="w-full p-3 rounded-xl input-dark text-sm">
                            <option value="Faible">Faible</option>
                            <option value="Moyen" selected>Moyen</option>
                            <option value="Élevé">Élevé</option>
                            <option value="Critique">Critique</option>
                        </select>
                    </div>
                    <textarea id="description" rows="3" placeholder="Description des faits précis..." class="w-full p-4 rounded-xl input-dark text-sm" required></textarea>
                    
                    <div class="pt-1">
                        <button type="button" id="locationBtn" class="w-full bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 font-semibold py-2.5 px-4 rounded-xl transition text-sm flex items-center justify-center gap-2">
                            <i class="fa-solid fa-location-dot"></i> <span id="btnText">Activer ma position</span>
                        </button>
                        <p id="locationStatus" class="text-center text-xs text-gray-500 mt-1.5"></p>
                    </div>

                    <div class="grid grid-cols-2 gap-3" id="geoFields" style="display: none;">
                        <input type="text" id="latitude" readonly class="w-full p-2.5 rounded-xl input-dark text-xs text-gray-400" placeholder="Latitude">
                        <input type="text" id="longitude" readonly class="w-full p-2.5 rounded-xl input-dark text-xs text-gray-400" placeholder="Longitude">
                    </div>
                </div>
            </div>
            <div>
                <h3 class="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3">2. Joindre une photo ou une vidéo</h3>
                <div onclick="document.getElementById('mediaInput').click()" class="border-2 border-dashed border-gray-700 hover:border-blue-500 bg-gray-900/30 rounded-2xl p-6 text-center cursor-pointer transition">
                    <input type="file" id="mediaInput" accept="image/*,video/*" class="hidden">
                    <i class="fa-solid fa-camera-rotate text-2xl text-gray-400 mb-2" id="mediaIcon"></i>
                    <p class="text-sm font-medium" id="mediaStatus">Chercher dans mes fichiers locaux</p>
                    <p class="text-xs text-gray-500 mt-1">Images, captures ou vidéos acceptées</p>
                </div>
            </div>
            <div>
                <h3 class="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3">3. Enregistrement vocal</h3>
                <div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 text-center">
                    <p class="text-xs text-gray-400 mb-3" id="audioStatus">Ajoutez un témoignage audio direct.</p>
                    <button type="button" id="recordBtn" class="w-14 h-14 bg-blue-600 hover:bg-blue-500 text-white rounded-full flex items-center justify-center mx-auto shadow-lg transition">
                        <i class="fa-solid fa-microphone text-xl" id="micIcon"></i>
                    </button>
                </div>
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl transition text-sm shadow-lg">
                Soumettre le signalement
            </button>
        </form>
    </div>
    <script>
        const mediaInput = document.getElementById('mediaInput');
        const mediaStatus = document.getElementById('mediaStatus');
        const mediaIcon = document.getElementById('mediaIcon');
        mediaInput.addEventListener('change', (e) => {
            if(e.target.files.length > 0) {
                mediaStatus.innerText = "Fichier sélectionné : " + e.target.files[0].name;
                mediaStatus.classList.add('text-blue-400');
                mediaIcon.className = "fa-solid fa-circle-check text-2xl text-green-400 mb-2";
            }
        });

        // Script de Géolocalisation
        document.getElementById('locationBtn').addEventListener('click', function() {
            const status = document.getElementById('locationStatus');
            const btnText = document.getElementById('btnText');
            const btn = this;

            if (!navigator.geolocation) {
                status.innerText = "✗ Non supporté par votre navigateur.";
                return;
            }

            btn.disabled = true;
            status.innerText = "⏳ Recherche de votre position...";

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude.toFixed(6);
                    const lng = position.coords.longitude.toFixed(6);
                    
                    document.getElementById('latitude').value = lat;
                    document.getElementById('longitude').value = lng;
                    document.getElementById('geoFields').style.style.display = 'grid';
                    
                    status.innerText = "✓ Position enregistrée.";
                    status.className = "text-center text-xs text-green-400 font-medium mt-1.5";
                    btnText.innerText = "Position synchronisée";
                    btn.disabled = false;
                },
                function() {
                    status.innerText = "✗ Impossible d'accéder à la position.";
                    status.className = "text-center text-xs text-red-400 font-medium mt-1.5";
                    btn.disabled = false;
                }
            );
        });

        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let audioBlob = null;
        const recordBtn = document.getElementById('recordBtn');
        const audioStatus = document.getElementById('audioStatus');
        const micIcon = document.getElementById('micIcon');
        recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        audioStatus.innerText = "Audio prêt pour l'envoi !";
                        audioStatus.className = "text-xs text-green-400 font-medium mb-3";
                    };
                    mediaRecorder.start();
                    isRecording = true;
                    recordBtn.classList.replace('bg-blue-600', 'bg-red-600');
                    micIcon.className = "fa-solid fa-stop text-xl animate-pulse";
                } catch (err) { alert("Microphone inaccessible ou refusé."); }
            } else {
                mediaRecorder.stop();
                isRecording = false;
                recordBtn.classList.replace('bg-red-600', 'bg-blue-600');
                micIcon.className = "fa-solid fa-microphone text-xl";
            }
        });

        document.getElementById('reportForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('title', document.getElementById('title').value);
            formData.append('description', document.getElementById('description').value);
            formData.append('category', document.getElementById('category').value);
            formData.append('severity', document.getElementById('severity').value);
            
            // Forcer la valeur 'Oui' pour l'anonymat par défaut (évite le bug VARCHAR(3) Neon)
            formData.append('anonyme', 'Oui');

            const lat = document.getElementById('latitude').value;
            const lng = document.getElementById('longitude').value;
            if(lat && lng) {
                formData.append('latitude', lat);
                formData.append('longitude', lng);
            }

            if(mediaInput.files[0]) { formData.append('media_file', mediaInput.files[0]); }
            if(audioBlob) { formData.append('audio_file', audioBlob, 'audio.wav'); }
            
            try {
                const response = await fetch('/api/reports', { method: 'POST', body: formData });
                const result = await response.json();
                if(result.success) {
                    alert("Signalement enregistré avec succès dans Neon.tech !");
                    location.reload();
                } else { alert("Erreur : " + result.error); }
            } catch (err) { alert("Erreur de connexion avec le serveur."); }
        });
    </script>
</body>
</html>"""
    
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            'success': True,
            'app': 'Signalement - Whistleblower Reporting API',
            'version': '1.0.0',
            'endpoints': {
                'reports': '/api/reports',
                'categories': '/api/categories',
                'severities': '/api/severities',
                'statuses': '/api/statuses',
                'statistics': '/api/reports/stats/summary',
                'media': '/api/media',
                'health': '/health'
            }
        }), 200

    # ==================== Initialisation au Démarrage (Pour Render/Gunicorn) ====================
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully in App Context")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")

        try:
            ExcelHelper.init_excel()
            logger.info("Excel ledger initialized successfully in App Context")
        except Exception as e:
            logger.error(f"Failed to initialize Excel file: {str(e)}")
    
    return app


# ==================== Point d'entrée de l'application ====================
# On instancie l'application globalement pour que Gunicorn puisse la trouver
app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)