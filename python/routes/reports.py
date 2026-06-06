import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from models import db, Report, AuditLog
from utils.excel_helper import ExcelHelper

logger = logging.getLogger(__name__)

# Définition du blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def create_audit_log(report_id, action, changes=None, performed_by='system'):
    """Helper pour créer les entrées de log d'audit (sans commit automatique)"""
    try:
        log = AuditLog(
            report_id=report_id,
            action=action,
            changes=json.dumps(changes) if changes else None,
            performed_by=performed_by
        )
        db.session.add(log)
        # NE PAS commiter ici, on laissera la route principale le faire globalement.
    except Exception as e:
        logger.error(f"Error creating audit log entry: {str(e)}")

# ==================== Routes des Rapports ====================

@api_bp.route('/reports', methods=['GET'])
def get_reports():
    """Récupérer tous les rapports avec pagination et filtres"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None)
        category = request.args.get('category', None)
        
        query = Report.query
        
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        
        # Tri par le plus récent
        query = query.order_by(Report.timestamp.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'reports': [r.to_dict() for r in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Récupérer un rapport spécifique"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        return jsonify({
            'success': True,
           @api_bp.route('/reports', methods=['POST'])
def create_report():
    """Créer un nouveau rapport avec support des fichiers audio et média"""
    try:
        # 1. Récupération des données du formulaire
        data = request.form
        
        required_fields = ['title', 'description', 'category', 'severity']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        audio_uri = None
        media_uri = None

        # 2. Gestion de la Photo / Vidéo locale
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file.filename != '':
                filename = secure_filename(f"media_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                file.save(filepath)
                media_uri = filepath

        # 3. Gestion du Message Vocal locale
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            if file.filename != '':
                filename = secure_filename(f"audio_{datetime.utcnow().timestamp()}.wav")
                filepath = os.path.join(current_app.config['AUDIO_FOLDER'], filename)
                file.save(filepath)
                audio_uri = filepath

        # 4. Conversion et nettoyage sécurisé des coordonnées géographiques
        lat_raw = data.get('latitude')
        lng_raw = data.get('longitude')

        latitude_val = float(str(lat_raw).replace(',', '.')) if lat_raw and str(lat_raw).strip() != "" else None
        longitude_val = float(str(lng_raw).replace(',', '.')) if lng_raw and str(lng_raw).strip() != "" else None

        # 5. Gestion de la chaîne Anonyme limitée à VARCHAR(3)
        raw_anonymous = data.get('is_anonymous', True)
        if raw_anonymous in [True, 'true', 'True', 'Oui', 'oui']:
            anonyme_db = 'Oui'
        else:
            anonyme_db = 'Non'

        # 6. Initialisation propre de l'objet unique Report
        report = Report(
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            severity=data.get('severity'),
            is_anonymous=anonyme_db,
            audio_uri=audio_uri,
            media_uri=media_uri,
            latitude=latitude_val,
            longitude=longitude_val,
            location_address=data.get('location_address'),
            status="Nouveau"
        )
        
        # On ajoute le rapport à la session
        db.session.add(report)
        
        # MAGIE : flush() envoie l'ordre à Neon mais ne ferme pas la transaction.
        # Cela force PostgreSQL à attribuer l'ID auto-incrémenté (ex: 4) à 'report.id'
        db.session.flush() 
        
        # Création du log d'audit relié au nouvel ID auto-généré en toute sécurité
        create_audit_log(report.id, 'created', {'status': 'Nouveau'})
        
        # On valide définitivement l'ensemble de la transaction (Rapport + Audit Log)
        db.session.commit()
        
        # Enregistrement synchrone dans Excel après la validation SQL
        try:
            ExcelHelper.update_or_add_report(report)
        except Exception as e:
            logger.error(f"Erreur d'écriture Excel lors de la création : {str(e)}")
        
        return jsonify({
            'success': True, 
            'message': 'Report created successfully', 
            'report': report.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()  # En cas d'erreur, on annule tout proprement
        logger.error(f"Error creating report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
            latitude=latitude_val,
            longitude=longitude_val,
            location_address=data.get('location_address'),
            status="Nouveau"
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Enregistrement synchrone dans Excel
        try:
            ExcelHelper.update_or_add_report(report)
        except Exception as e:
            logger.error(f"Erreur d'écriture Excel lors de la création : {str(e)}")
        
        # Création du log d'audit relié au nouvel ID auto-généré
        create_audit_log(report.id, 'created', {'status': 'Nouveau'})
        
        return jsonify({
            'success': True, 
            'message': 'Report created successfully', 
            'report': report.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error creating report: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Mettre à jour un rapport"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        data = request.get_json()
        changes = {}
        
        updatable_fields = [
            'title', 'description', 'category', 'severity', 'location_address', 
            'latitude', 'longitude', 'is_anonymous', 'reporter_name', 
            'reporter_email', 'reporter_phone', 'status', 'admin_notes'
        ]
        
        # Détection des changements
        for field in updatable_fields:
            if field in data:
                old_value = getattr(report, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    # Gestion spécifique de l'anonymat en PUT si envoyé sous forme de booléen
                    if field == 'is_anonymous':
                        setattr(report, field, 'Oui' if new_value in [True, 'true', 'Oui'] else 'Non')
                    else:
                        setattr(report, field, new_value)
        
        if changes:
            db.session.commit()
            
            # Enregistrement dans Excel
            try:
                ExcelHelper.update_or_add_report(report)
            except Exception as e:
                logger.error(f"Erreur d'écriture Excel lors de la modification : {str(e)}")
                
            create_audit_log(report.id, 'updated', changes)
        
        return jsonify({
            'success': True,
            'report': report.to_dict(),
            'message': 'Report updated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error updating report: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Supprimer un rapport"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Suppression des fichiers physiques liés (si existants)
        if report.audio_uri and os.path.exists(report.audio_uri):
            os.remove(report.audio_uri)
        if report.media_uri and os.path.exists(report.media_uri):
            os.remove(report.media_uri)
        
        # Nettoyage de l'historique d'audit pour éviter les contraintes de clés étrangères
        AuditLog.query.filter_by(report_id=report_id).delete()
        
        db.session.delete(report)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Routes de Statistiques & Référentiels ====================

@api_bp.route('/reports/stats/summary', methods=['GET'])
def get_stats_summary():
    """Obtenir les statistiques globales (Optimisé en SQL)"""
    try:
        total_reports = Report.query.count()
        
        by_status = {}
        by_category = {}
        
        # On ne charge que les colonnes nécessaires pour économiser la RAM
        reports_data = db.session.query(Report.status, Report.category).all()
        for status, category in reports_data:
            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
        
        return jsonify({
            'success': True,
            'total_reports': total_reports,
            'by_status': by_status,
            'by_category': by_category
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify({
        'success': True, 
        'categories': [
            {'value': 'Sécurité', 'label': 'Sécurité'},
            {'value': 'Environnement', 'label': 'Environnement'},
            {'value': 'Corruption', 'label': 'Corruption'},
            {'value': 'Santé publique', 'label': 'Santé publique'},
            {'value': 'Autre', 'label': 'Autre'}
        ]
    }), 200


@api_bp.route('/severities', methods=['GET'])
def get_severities():
    return jsonify({
        'success': True, 
        'severities': [
            {'value': 'Faible', 'label': 'Faible'},
            {'value': 'Moyen', 'label': 'Moyen'},
            {'value': 'Élevé', 'label': 'Élevé'},
            {'value': 'Critique', 'label': 'Critique'}
        ]
    }), 200


@api_bp.route('/statuses', methods=['GET'])
def get_statuses():
    return jsonify({
        'success': True, 
        'statuses': [
            {'value': 'Nouveau', 'label': 'Nouveau'},
            {'value': 'En cours', 'label': 'En cours'},
            {'value': 'Traité', 'label': 'Traité'},
            {'value': 'Rejeté', 'label': 'Rejeté'}
        ]
    }), 200