"""
Routes simplifiées pour la gestion des réunions
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Path
from fastapi.logger import logger
from typing import Optional, Dict, Any, List
import asyncio
import asyncio
import os
from datetime import datetime
import logging
import traceback

from ..core.security import get_current_user
from ..services.assemblyai import transcribe_meeting, check_transcription_status
from ..db.postgres_meetings import (
    create_meeting_async,
    get_meeting_async,
    get_meetings_by_user_async,
    update_meeting_async,
    delete_meeting_async,
    get_meeting_speakers_async,
)
from ..core.config import settings
# On s'appuie sur la tâche périodique interne pour les mises à jour de statut

# Configuration du logging
logger = logging.getLogger("meeting-transcriber")

router = APIRouter(prefix="/simple/meetings", tags=["Réunions Simplifiées"])

@router.post("/upload", response_model=dict, status_code=200)
async def upload_meeting(
    file: UploadFile = File(..., description="Fichier audio à transcrire"),
    title: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Télécharge un fichier audio et crée une nouvelle réunion avec transcription simplifiée.
    
    - **file**: Fichier audio à transcrire
    - **title**: Titre optionnel de la réunion (utilisera le nom du fichier par défaut)
    
    La transcription est lancée immédiatement en arrière-plan et peut prendre du temps
    en fonction de la durée de l'audio. Le statut de la transcription est automatiquement
    vérifié et mis à jour.
    """
    try:
        # Utiliser le titre ou le nom du fichier par défaut
        if not title:
            title = file.filename
            
        # 1. Sauvegarder le fichier audio
        user_upload_dir = os.path.join("uploads", str(current_user["id"]))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(user_upload_dir, filename)
        
        # Lire et sauvegarder le contenu du fichier
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 2. Créer l'entrée dans la base de données avec le statut "processing" dès le début
        file_url = f"/{file_path}"
        meeting_data = {
            "title": title,
            "file_url": file_url,
            "transcript_status": "processing",  # Commencer directement en processing au lieu de pending
            "success": True  # Ajouter un indicateur de succès pour la cohérence avec les autres endpoints
        }
        meeting = await create_meeting_async(meeting_data, current_user["id"])  # async direct
        logger.info(f"Réunion créée avec le statut 'processing': {meeting['id']}")
        
        # 3. Lancer la transcription en arrière-plan (appel bloquant déporté en thread)
        transcript_id = await asyncio.to_thread(transcribe_meeting, meeting["id"], file_url, current_user["id"]) 
        logger.info(f"Transcription lancée pour la réunion {meeting['id']} avec l'ID de transcription {transcript_id}")
        
        # 4. Enregistrer l'ID de transcription ou marquer l'erreur
        if transcript_id:
            await update_meeting_async(meeting["id"], current_user["id"], {"transcript_id": transcript_id})
        else:
            await update_meeting_async(meeting["id"], current_user["id"], {
                "transcript_status": "error",
                "transcript_text": "Échec du démarrage de la transcription (voir logs)."
            })
        
        return meeting
    
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de la réunion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur s'est produite lors de l'upload: {str(e)}"
        )

# La vérification périodique est gérée par une tâche dédiée au sein de l'API

@router.post("/{meeting_id}/transcribe", response_model=dict)
async def simple_transcribe_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        meeting = await get_meeting_async(meeting_id, current_user["id"])
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")

        file_url = meeting.get("file_url")
        if not file_url:
            await update_meeting_async(meeting_id, current_user["id"], {
                "transcript_status": "error",
                "transcript_text": "Aucun fichier associé à cette réunion"
            })
            return await get_meeting_async(meeting_id, current_user["id"])

        tid = await asyncio.to_thread(transcribe_meeting, meeting_id, file_url, current_user["id"])  
        if tid:
            await update_meeting_async(meeting_id, current_user["id"], {
                "transcript_id": tid,
                "transcript_status": "processing",
                "transcript_text": f"Transcription en cours avec ID: {tid}"
            })
        else:
            await update_meeting_async(meeting_id, current_user["id"], {
                "transcript_status": "error",
                "transcript_text": "Échec du démarrage de la transcription (voir logs)."
            })

        return await get_meeting_async(meeting_id, current_user["id"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de la transcription: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du démarrage de la transcription")

@router.post("/{meeting_id}/retry-transcription", response_model=dict)
async def simple_retry_transcription(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await simple_transcribe_meeting(meeting_id, current_user)

@router.get("/", response_model=list)
async def list_meetings(
    status: Optional[str] = Query(None, description="Filtrer par statut de transcription"),
    current_user: dict = Depends(get_current_user)
):
    """
    Liste toutes les réunions de l'utilisateur.
    
    - **status**: Filtre optionnel pour afficher uniquement les réunions avec un statut spécifique
    
    Retourne une liste de réunions avec leurs métadonnées.
    """
    meetings = await get_meetings_by_user_async(current_user["id"], status)
    return meetings

@router.get("/{meeting_id}", response_model=dict)
async def get_meeting_details(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les détails d'une réunion spécifique.
    
    - **meeting_id**: Identifiant unique de la réunion
    
    Retourne toutes les informations de la réunion, y compris le texte de transcription
    si la transcription est terminée.
    """
    try:
        logger.info(f"Tentative de récupération des détails de la réunion {meeting_id} par l'utilisateur {current_user['id']}")
        
        # Récupérer les détails de la réunion
        meeting = await get_meeting_async(meeting_id, current_user["id"]) 
        
        if not meeting:
            logger.warning(f"Réunion {meeting_id} non trouvée pour l'utilisateur {current_user['id']}")
            return {
                "status": "not_found",
                "message": "Réunion non trouvée ou supprimée",
                "id": meeting_id,
                "deleted": True,
                "transcript_status": "deleted",  # Ajouter cette propriété pour éviter l'erreur côté frontend
                "success": False
            }
        
        # Si la transcription est en cours et qu'on a un transcript_id, vérifier immédiatement auprès d'AssemblyAI
        if meeting.get("transcript_status") == "processing" and meeting.get("transcript_id"):
            try:
                tid = meeting.get("transcript_id")
                status_data = await asyncio.to_thread(check_transcription_status, tid)
                if isinstance(status_data, dict) and status_data.get("status") == "completed":
                    transcript_text = status_data.get("text", "")
                    audio_duration = int(status_data.get("audio_duration", 0) or 0)
                    speakers_count = 1
                    if status_data.get("utterances"):
                        speakers_set = set()
                        for u in status_data.get("utterances", []) or []:
                            speakers_set.add(u.get("speaker", "Unknown"))
                        speakers_count = len(speakers_set) or 1
                    await update_meeting_async(meeting_id, current_user["id"], {
                        "transcript_status": "completed",
                        "transcript_text": transcript_text,
                        "duration_seconds": audio_duration,
                        "speakers_count": speakers_count,
                    })
                    # Rafraîchir l'objet meeting après update
                    meeting = await get_meeting_async(meeting_id, current_user["id"]) 
            except Exception as _e:
                logger.warning(f"Vérification immédiate AssemblyAI échouée pour {meeting_id}: {_e}")
        
        # Appliquer les noms personnalisés des speakers à la transcription si elle est complétée
        if meeting.get("transcript_status") == "completed" and meeting.get("transcript_id"):
            try:
                from ..services.transcription_checker import get_assemblyai_transcript_details, format_transcript_text
                
                logger.info(f"Application des noms personnalisés à la transcription pour la réunion {meeting_id}")
                from ..db.postgres_meetings import get_meeting_speakers
                speakers_data = await get_meeting_speakers_async(meeting_id, current_user["id"]) or []
                
                # S'il existe des speakers personnalisés, formater la transcription avec ces noms
                if speakers_data and any(speaker.get("custom_name") for speaker in speakers_data):
                    transcript_id = meeting.get("transcript_id")
                    transcript_data = await asyncio.to_thread(get_assemblyai_transcript_details, transcript_id)
                    
                    if transcript_data:
                        speaker_names = {speaker["speaker_id"]: speaker["custom_name"] for speaker in speakers_data if speaker.get("custom_name")}
                        logger.info(f"Noms personnalisés détectés: {speaker_names}")
                        
                        if speaker_names:
                            updated_transcript = format_transcript_text(transcript_data, speaker_names)
                            meeting["transcript_text"] = updated_transcript
                            logger.info(f"Transcription mise à jour avec {len(speaker_names)} noms personnalisés")
            except Exception as e:
                logger.error(f"Erreur lors de l'application des noms personnalisés: {str(e)}")
        
        # Déclenchement auto du résumé si la transcription est terminée mais aucun résumé présent
        try:
            should_start_summary = (
                meeting.get("transcript_status") == "completed"
                and not meeting.get("summary_text")
                and (meeting.get("summary_status") in (None, "not_generated", "error") )
            )
            if should_start_summary:
                from ..services.mistral_summary import process_meeting_summary_async
                logger.info(f"Déclenchement automatique du résumé pour {meeting_id}")
                # Marquer en processing et lancer en arrière-plan
                await update_meeting_async(meeting_id, current_user["id"], {"summary_status": "processing"})
                asyncio.create_task(process_meeting_summary_async(meeting_id, current_user["id"]))
                # Rafraîchir l'objet meeting pour refléter le nouveau statut
                meeting = await get_meeting_async(meeting_id, current_user["id"]) 
        except Exception as e:
            logger.warning(f"Échec du déclenchement auto du résumé pour {meeting_id}: {e}")
        
        # Ajouter des informations supplémentaires pour faciliter le débogage côté frontend
        meeting["status"] = "success"
        meeting["success"] = True
        meeting["deleted"] = False
        
        return meeting
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails de la réunion {meeting_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Une erreur s'est produite lors de la récupération des détails: {str(e)}",
            "id": meeting_id,
            "deleted": False,
            "transcript_status": "error",  # Ajouter cette propriété pour éviter l'erreur côté frontend
            "success": False
        }

@router.delete("/{meeting_id}", response_model=dict)
async def delete_simple_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprime une réunion et ses données associées.
    
    - **meeting_id**: Identifiant unique de la réunion
    
    Cette opération supprime à la fois les métadonnées de la réunion et le fichier audio associé.
    """
    try:
        logger.info(f"Tentative de suppression de la réunion {meeting_id} par l'utilisateur {current_user['id']}")
        
        # Récupérer la réunion pour vérifier qu'elle existe et appartient à l'utilisateur
        meeting = await get_meeting_async(meeting_id, current_user["id"]) 
        
        if not meeting:
            logger.warning(f"Réunion {meeting_id} non trouvée pour l'utilisateur {current_user['id']}")
            return {
                "status": "not_found",
                "message": "Réunion non trouvée ou déjà supprimée",
                "id": meeting_id,
                "success": False
            }
        
        # Supprimer la réunion de la base de données
        result = await delete_meeting_async(meeting_id, current_user["id"]) 
        
        if not result:
            logger.error(f"Échec de la suppression de la réunion {meeting_id}")
            return {
                "status": "error",
                "message": "Erreur lors de la suppression de la réunion",
                "id": meeting_id,
                "success": False
            }
        
        # Supprimer le fichier audio si possible
        try:
            file_path = meeting.get("file_url", "").lstrip("/")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Fichier audio supprimé: {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier audio: {str(e)}")
            # Ne pas faire échouer l'opération si la suppression du fichier échoue
        
        logger.info(f"Réunion {meeting_id} supprimée avec succès")
        return {
            "status": "success",
            "message": "Réunion supprimée avec succès",
            "id": meeting_id,
            "success": True,
            "meeting_data": {
                "id": meeting_id,
                "title": meeting.get("title", ""),
                "deleted": True,
                "transcript_status": "deleted"
            }
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la réunion {meeting_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Une erreur s'est produite lors de la suppression: {str(e)}",
            "id": meeting_id,
            "success": False
        }
