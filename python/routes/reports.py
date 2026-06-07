import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# Importation du SDK Cloudinary
import cloudinary
import cloudinary.uploader

from models import db, Report, AuditLog
from utils.excel_helper import ExcelHelper

logger = logging.getLogger(__name__)

# Définition du blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Configuration automatique du SDK Cloudinary via la variable d'environnement CLOUDINARY_URL
cloudinary.config(secure=True)

def create_audit_log_safely(report_obj, action, changes=None, performed_by='system'):
    """Helper associant directement l'objet Report au log d'audit pour éviter les violations de clé"""
    try:
        log = AuditLog(
            report=report_obj,  # Liaison par objet ORM (SQLAlchemy gère l'ordre d'insertion)
            action=action,
            changes=json.dumps(changes) if changes else None,
            performed_by=performed_by
        )
        db.session.add(log)
    except Exception as e:
        logger.error(f"Error creating audit log: {str(e)}")

# ==================== Routes des Rapports ====================

@api_bp.route('/reports', methods=['POST'])
def create_report():
    """Créer un nouveau rapport avec téléversement Cloudinary et liaison ORM sécurisée"""
    try:
        # 1. Récupération des données du formulaire
        data = request.form
        
        required_fields = ['title', 'description', 'category', 'severity']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        audio_uri = None
        media_uri = None

        # 2. Gestion de la Photo / Vidéo avec Cloudinary
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file.filename != '':
                try:
                    # Envoi direct du flux binaire vers Cloudinary
                    upload_result = cloudinary.uploader.upload(
                        file,
                        resource_type="auto",  # Détecte automatiquement les images et vidéos
                        folder="alerte_citoyenne/medias"
                    )
                    # Récupération de l'URL sécurisée HTTPS de Cloudinary
                    media_uri = upload_result.get('secure_url')
                except Exception as upload_err:
                    logger.error(f"Erreur d'upload média Cloudinary: {str(upload_err)}")
                    return jsonify({'success': False, 'error': f"Media upload failed: {str(upload_err)}"}), 500

        # 3. Gestion du Message Vocal avec Cloudinary
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            if file.filename != '':
                try:
                    # Cloudinary traite les fichiers audio sous la catégorie "video"
                    upload_audio_result = cloudinary.uploader.upload(
                        file,
                        resource_type="video",
                        folder="alerte_citoyenne/audios"
                    )
                    # Récupération de l'URL sécurisée HTTPS de Cloudinary
                    audio_uri = upload_audio_result.get('secure_url')
                except Exception as upload_err:
                    logger.error(f"Erreur d'upload audio Cloudinary: {str(upload_err)}")
                    return jsonify({'success': False, 'error': f"Audio upload failed: {str(upload_err)}"}), 500

        # 4. Conversion et nettoyage des coordonnées géographiques
        lat_raw = data.get('latitude')
        lng_raw = data.get('longitude')

        latitude_val = float(str(lat_raw).replace(',', '.')) if lat_raw and str(lat_raw).strip() != "" else None
        longitude_val = float(str(lng_raw).replace(',', '.')) if lng_raw and str(lng_raw).strip() != "" else None

        # 5. Gestion de l'Anonymat
        raw_anonymous = data.get('is_anonymous', True)
        anonyme_db = 'Oui' if raw_anonymous in [True, 'true', 'True', 'Oui', 'oui'] else 'Non'

        # 6. Initialisation de l'objet Report
        report = Report(
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            severity=data.get('severity'),
            is_anonymous=anonyme_db,
            audio_uri=audio_uri,  # Contient désormais l'URL Cloudinary (https://res.cloudinary.com/...)
            media_uri=media_uri,  # Contient désormais l'URL Cloudinary (https://res.cloudinary.com/...)
            latitude=latitude_val,
            longitude=longitude_val,
            location_address=data.get('location_address'),
            status="Nouveau"
        )
        
        # On ajoute le rapport à la session
        db.session.add(report)
        
        # 7. Création de l'audit lié par l'objet relationnel
        create_audit_log_safely(report, 'created', {'status': 'Nouveau'})
        
        # 8. Un seul commit pour valider de manière atomique le Report et l'Audit
        db.session.commit()
        
        # 9. Enregistrement Excel isolé (ne bloque pas la route s'il échoue)
        try:
            ExcelHelper.update_or_add_report(report)
        except Exception as e:
            logger.error(f"Erreur d'écriture Excel isolée : {str(e)}")
        
        return jsonify({
            'success': True, 
            'message': 'Report created successfully', 
            'report': report.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()  # Nettoyage en cas d'échec total
        logger.error(f"Error creating report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
            'report': report.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
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
        
        for field in updatable_fields:
            if field in data:
                old_value = getattr(report, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    if field == 'is_anonymous':
                        setattr(report, field, 'Oui' if new_value in [True, 'true', 'Oui'] else 'Non')
                    else:
                        setattr(report, field, new_value)
        
        if changes:
            create_audit_log_safely(report, 'updated', changes)
            db.session.commit()
            
            try:
                ExcelHelper.update_or_add_report(report)
            except Exception as e:
                logger.error(f"Erreur d'écriture Excel lors de la modification : {str(e)}")
        
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
        
        # Suppression des assets Cloudinary s'ils existent avant de supprimer l'enregistrement
        # Note : On extrait l'ID public de Cloudinary si vous souhaitez une suppression complète sur le cloud.
        # Pour l'instant, nous supprimons uniquement les références locales historiques s'il en restait.
        if report.audio_uri and os.path.exists(report.audio_uri):
            os.remove(report.audio_uri)
        if report.media_uri and os.path.exists(report.media_uri):
            os.remove(report.media_uri)
        
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
    try:
        total_reports = Report.query.count()
        by_status = {}
        by_category = {}
        
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