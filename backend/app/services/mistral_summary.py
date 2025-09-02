import json
import logging
import os
from typing import Optional, Dict, Any
import asyncio
from ..core.config import settings
import requests

# Configuration pour Mistral AI
# Lire la clé via les settings/env
MISTRAL_API_KEY = settings.MISTRAL_API_KEY
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Configuration du logging
logger = logging.getLogger("meeting-transcriber")

def get_client_template(client_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional[str]:
    """
    Récupère le template de résumé associé à un client.
    
    Args:
        client_id: ID du client (optionnel)
        user_id: ID de l'utilisateur propriétaire du client (optionnel)
        
    Returns:
        str: Template de résumé ou None si aucun template n'est trouvé
    """
    if not client_id or not user_id:
        return None
        
    try:
        # Importer les fonctions ici pour éviter les imports circulaires
        from ..db.client_queries import get_client
        
        # Récupérer les informations du client
        client = get_client(client_id, user_id)
        
        if client and client.get("summary_template"):
            logger.info(f"Template de résumé trouvé pour le client {client_id}")
            return client["summary_template"]
        else:
            logger.info(f"Aucun template de résumé trouvé pour le client {client_id}")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du template client: {str(e)}")
        return None

def generate_meeting_summary(
    transcript_text: str,
    meeting_title: Optional[str] = None,
    client_id: Optional[str] = None,
    user_id: Optional[str] = None,
    template_type: Optional[str] = None,
) -> Optional[str]:
    """
    Génère un compte rendu de réunion à partir d'une transcription en utilisant l'API Mistral.
    
    Args:
        transcript_text: Texte de la transcription de la réunion
        meeting_title: Titre de la réunion (optionnel)
        client_id: ID du client pour personnaliser le résumé (optionnel)
        user_id: ID de l'utilisateur qui demande le résumé (optionnel)
        
    Returns:
        str: Compte rendu généré ou None en cas d'erreur
    """
    if not MISTRAL_API_KEY:
        logger.error("Clé API Mistral non configurée. Impossible de générer le compte rendu.")
        return None
        
    try:
        # Vérifier s'il existe un template client personnalisé
        client_template = None
        if client_id and user_id:
            client_template = get_client_template(client_id, user_id)
        
        title_part = f" intitulée '{meeting_title}'" if meeting_title else ""
        
        # Préparer prompts intégrés
        formation_prompt = f"""Objectif :
À partir d'une transcription d'une session de formation, produire un compte rendu orienté apprentissages.

FORMAT EXACT ATTENDU :

# 🎓 Session de formation{f" — '{meeting_title}'" if meeting_title else ''}

- 👥 **Participants** : [Liste]
- 🧑‍🏫 **Formateur** : [Nom si identifiable]
- 🕒 **Durée estimée** : [Durée si mentionnée]

---

## 🧠 Objectifs pédagogiques
- [Objectif 1]
- [Objectif 2]

---

## 📌 Points clés appris
- [Point 1]
- [Point 2]

---

## 🧪 Exercices / Démonstrations
| Exercice | Compétences visées | Résultat |
|----------|--------------------|----------|
| [Nom] | [Compétences] | [Résultat] |

---

## ❓ Questions fréquentes et réponses
- Q: [Question]  
  R: [Réponse]

---

## 🔜 Actions / Pratique recommandée
- [Action 1]
- [Action 2]

---

## 📚 Ressources
- [Ressource 1]
- [Ressource 2]

Consigne importante: REMPLACE tous les placeholders par les informations réelles extraites de la transcription. Si une info manque, indiquer clairement "Non mentionné" sans garder de crochets.

Transcription :

{transcript_text}
"""

        # Utiliser le template personnalisé s'il existe, sinon utiliser un template intégré (formation) ou par défaut
        if client_template:
            # Remplacer les variables dans le template client
            prompt = client_template.replace("{transcript_text}", transcript_text)
            if meeting_title:
                prompt = prompt.replace("{meeting_title}", meeting_title)
            logger.info("Utilisation d'un template client personnalisé")
        elif template_type and template_type.lower() == "formation":
            prompt = formation_prompt
            logger.info("Utilisation du template intégré: formation")
        else:
            # Template par défaut
            prompt = f"""Objectif :
À partir d'une transcription brute d'une réunion, produire un compte rendu EXACTEMENT selon le format d'exemple fourni ci-dessous, intégrant précisément les emojis, les titres, les tableaux, et le style montrés.

VOICI UN EXEMPLE EXACT DU FORMAT DE SORTIE QUE TU DOIS REPRODUIRE :

# 📅 Réunion du [date inconnue ou date exacte si mentionnée] u2014 [Titre de la réunion ou sujet principal]

- 👥 **Participants** : [Liste des participants]
- ✏️ **Animateur/trice** : [Nom de l'animateur si identifiable]
- 🕒 **Durée estimée** : [Durée si mentionnée]

---

## 🧠 Résumé express
Un paragraphe de 3-4 lignes résumant l'essentiel de la réunion.

---

## 🗂️ Ordre du jour *(reconstruit)*
1. 📡 [Premier point]
2. 💰 [Deuxième point]
3. 👤 [Troisième point]
4. ⏱️ [Quatrième point]

---

## ✅ Décisions prises
- 🔒 [Décision 1] *([Nom de la personne])*
- 💰 [Décision 2] *([Nom de la personne])*
- 👥 [Décision 3] *([Nom de la personne])*

---

## 🔜 Tâches & actions à suivre

| 📌 Tâche | 👤 Responsable | ⏳ Échéance | 🔗 Liée à |
|------------------|----------------|----------------|-----------|
| [Description tâche 1] | [Responsable] | [Échéance] | [Lien] |
| [Description tâche 2] | [Responsable] | [Échéance] | [Lien] |

---

## ⚠️ Points de vigilance
- ⚠️ [Point de vigilance 1]
- 🔄 [Point de vigilance 2]

---

## 🧵 Sujets abordés

| 💬 Sujet | 🗣️ Intervenants |
|-------------|------------------------|
| [Sujet 1] | [Liste des intervenants] |
| [Sujet 2] | [Liste des intervenants] |
| [Sujet 3] | [Liste des intervenants] |
| [Sujet 4] | [Liste des intervenants] |

---

## 📚 Ressources mentionnées
- [Ressource 1]
- [Ressource 2]
- [Ressource 3]

---

## 🗓️ Prochaine réunion
📍 [Date et heure de la prochaine réunion si mentionnée]

UTILISE EXACTEMENT CE FORMAT, avec les mêmes emojis et la même mise en page, mais REMPLACE TOUS LES PLACEHOLDERS ENTRE CROCHETS par les informations réelles extraites de la transcription. Ne laisse AUCUN texte du type '[Premier point]' ou '[Sujet 1]' dans ta réponse. Si tu n'as pas l'information pour une section, indique-le clairement (ex: "Non mentionné" ou "Aucun point identifié"), mais NE CONSERVE PAS les placeholders entre crochets.

Voici la transcription d'une réunion{title_part} :

{transcript_text}
"""        
        # Préparer la requête pour l'API Mistral
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        
        payload = {
            "model": "mistral-large-latest",  # Utiliser le modèle le plus récent et le plus performant
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Température basse pour des résultats plus cohérents
            "max_tokens": 4000  # Limite de tokens pour la réponse
        }
        
        # Envoyer la requête à l'API Mistral
        logger.info("Envoi de la requête à l'API Mistral pour générer un compte rendu")
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        
        # Vérifier la réponse
        if response.status_code == 200:
            response_data = response.json()
            summary = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if summary:
                logger.info("Compte rendu généré avec succès par l'API Mistral")
                return summary
            else:
                logger.error("La réponse de l'API Mistral ne contient pas de contenu")
                return None
        else:
            logger.error(f"Erreur lors de l'appel à l'API Mistral: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du compte rendu: {str(e)}")
        return None

def process_meeting_summary(meeting_id: str, user_id: str, client_id: Optional[str] = None, async_mode: bool = False):
    """
    Traite la génération du compte rendu pour une réunion spécifique.
    
    Cette fonction récupère la transcription, génère le compte rendu et met à jour la base de données.
    
    Args:
        meeting_id: Identifiant de la réunion
        user_id: Identifiant de l'utilisateur
        client_id: Identifiant du client pour personnaliser le résumé (optionnel)
        async_mode: Si True, retourne immédiatement après avoir mis à jour le statut (pour API)
    
    Returns:
        bool: True si le traitement a réussi, False sinon
    """
    from ..db.postgres_meetings import get_meeting, update_meeting, get_meeting_speakers
    from ..services.transcription_checker import get_assemblyai_transcript_details, replace_speaker_names_in_text
    
    try:
        # Récupérer les données de la réunion
        meeting = get_meeting(meeting_id, user_id)
        if not meeting:
            logger.error(f"Réunion {meeting_id} non trouvée pour l'utilisateur {user_id}")
            return False
        
        # Vérifier que nous avons une transcription
        transcript_text = meeting.get("transcript_text")
        if not transcript_text:
            logger.error(f"Aucune transcription disponible pour la réunion {meeting_id}")
            return False
        
        # Récupérer les noms personnalisés des locuteurs
        speakers_data = get_meeting_speakers(meeting_id, user_id)
        speaker_names = {}
        if speakers_data:
            for speaker in speakers_data:
                speaker_names[speaker['speaker_id']] = speaker['custom_name']
            logger.info(f"Noms personnalisés des locuteurs récupérés: {speaker_names}")
        
        # Utiliser la transcription avec les noms personnalisés si disponibles
        if speaker_names:
            formatted_transcript = replace_speaker_names_in_text(transcript_text, speaker_names)
            logger.info("Transcription formatée avec les noms personnalisés")
        else:
            formatted_transcript = transcript_text
            logger.info("Aucun nom personnalisé trouvé, utilisation de la transcription originale")
        
        # Mettre à jour le statut en "processing"
        update_meeting(meeting_id, user_id, {"summary_status": "processing"})
        
        if async_mode:
            logger.info(f"Mode asynchrone activé pour la réunion {meeting_id}, statut mis à jour")
            return True
        
        # Générer le compte rendu avec la transcription formatée
        logger.info(f"Génération du compte rendu pour la réunion {meeting_id}")
        summary_text = generate_meeting_summary(
            formatted_transcript,
            meeting.get("title", "Réunion"),
            client_id,
            user_id,
            None,
        )
        
        if summary_text:
            # Mettre à jour la base de données avec le compte rendu
            update_meeting(meeting_id, user_id, {
                "summary_text": summary_text,
                "summary_status": "completed"
            })
            logger.info(f"Compte rendu généré avec succès pour la réunion {meeting_id}")
            return True
        else:
            # Marquer comme erreur
            update_meeting(meeting_id, user_id, {"summary_status": "error"})
            logger.error(f"Échec de la génération du compte rendu pour la réunion {meeting_id}")
            return False
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement du compte rendu pour la réunion {meeting_id}: {str(e)}")
        try:
            update_meeting(meeting_id, user_id, {"summary_status": "error"})
        except:
            pass
        return False


async def process_meeting_summary_async(
    meeting_id: str,
    user_id: str,
    client_id: Optional[str] = None,
    template_type: Optional[str] = None,
) -> bool:
    """
    Version asynchrone sûre pour l'event loop principale: utilise les fonctions DB async
    et exécute l'appel bloquant à l'API Mistral dans un thread.
    """
    from ..db.postgres_meetings import get_meeting_async, update_meeting_async, get_meeting_speakers_async
    from ..services.transcription_checker import replace_speaker_names_in_text
    try:
        meeting = await get_meeting_async(meeting_id, user_id)
        if not meeting:
            logger.error(f"Réunion {meeting_id} non trouvée pour l'utilisateur {user_id}")
            return False

        transcript_text = meeting.get("transcript_text")
        if not transcript_text:
            logger.error(f"Aucune transcription disponible pour la réunion {meeting_id}")
            return False

        speakers_data = await get_meeting_speakers_async(meeting_id, user_id)
        speaker_names: Dict[str, str] = {}
        if speakers_data:
            for speaker in speakers_data:
                speaker_names[speaker['speaker_id']] = speaker['custom_name']

        formatted_transcript = replace_speaker_names_in_text(transcript_text, speaker_names) if speaker_names else transcript_text

        await update_meeting_async(meeting_id, user_id, {"summary_status": "processing"})

        # Appel Mistral (bloquant) déporté dans un thread
        summary_text = await asyncio.to_thread(
            generate_meeting_summary,
            formatted_transcript,
            meeting.get("title", "Réunion"),
            client_id,
            user_id,
            template_type,
        )

        if summary_text:
            await update_meeting_async(meeting_id, user_id, {
                "summary_text": summary_text,
                "summary_status": "completed",
            })
            return True
        else:
            await update_meeting_async(meeting_id, user_id, {"summary_status": "error"})
            return False
    except Exception as e:
        logger.error(f"[async] Erreur lors du traitement du compte rendu pour {meeting_id}: {e}")
        try:
            await update_meeting_async(meeting_id, user_id, {"summary_status": "error"})
        except Exception:
            pass
        return False
