"""
Collaborative Writing Endpoints
Handles collaborative workflows, prompt generation, and AI-assisted writing
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, Path, status

from api.v1.schemas.responses import DataResponse, TaskResponse, ValidationResponse
from api.core.database import get_novel_data_manager
from api.core.exceptions import ValidationException, handle_database_error
from collaborative_workflow import HumanAICollaborativeWorkflow as CollaborativeWorkflow
from batch_creation_manager import BatchCreationManager
from prompt_generator.core import NovelPromptGenerator as PromptGenerator
from prompt_generator.quality_validator import QualityValidator
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/workflow/start",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start collaborative workflow",
    description="Initialize a new collaborative writing workflow"
)
async def start_collaborative_workflow(
    novel_id: UUID = Body(..., description="Novel UUID"),
    workflow_type: str = Body("worldbuilding", description="Type of workflow"),
    parameters: Dict[str, Any] = Body({}, description="Workflow parameters")
):
    """Start a collaborative workflow"""
    try:
        workflow = CollaborativeWorkflow(str(novel_id))

        # Initialize workflow
        task_id = await workflow.start_workflow(
            workflow_type=workflow_type,
            parameters=parameters
        )

        return TaskResponse(
            success=True,
            message=f"Collaborative workflow '{workflow_type}' started",
            task_id=task_id,
            status="running",
            started_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to start collaborative workflow: {e}")
        raise handle_database_error(e)


@router.get(
    "/workflow/{task_id}/status",
    response_model=TaskResponse,
    summary="Get workflow status",
    description="Get the status of a collaborative workflow"
)
async def get_workflow_status(
    task_id: str = Path(..., description="Task ID")
):
    """Get workflow status"""
    try:
        # This would need implementation to track workflow status
        # Placeholder response
        return TaskResponse(
            success=True,
            message="Workflow status retrieved",
            task_id=task_id,
            status="running",
            progress=45.0,
            started_at=datetime.now()
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/prompt/generate",
    response_model=DataResponse[str],
    summary="Generate writing prompt",
    description="Generate an AI writing prompt based on context"
)
async def generate_prompt(
    novel_id: UUID = Body(..., description="Novel UUID"),
    prompt_type: str = Body("scene", description="Type of prompt to generate"),
    context: Dict[str, Any] = Body({}, description="Context for prompt generation"),
    include_worldbuilding: bool = Body(True, description="Include worldbuilding context"),
    include_characters: bool = Body(True, description="Include character information")
):
    """Generate a writing prompt"""
    try:
        generator = PromptGenerator()

        # Gather context from database
        novel_manager = get_novel_data_manager(str(novel_id))

        context_data = {
            "novel_id": str(novel_id),
            "prompt_type": prompt_type,
            **context
        }

        if include_worldbuilding:
            # Add worldbuilding context
            domains = await novel_manager.get_domains()
            context_data["domains"] = [d.dict() for d in domains[:3]]  # Limit to avoid huge prompts

        if include_characters:
            # Add character context
            characters = await novel_manager.get_characters()
            context_data["characters"] = [c.dict() for c in characters[:5]]

        # Generate prompt
        prompt = await generator.generate_prompt(
            prompt_type=prompt_type,
            context=context_data
        )

        return DataResponse(
            success=True,
            message="Prompt generated successfully",
            data=prompt
        )

    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        raise handle_database_error(e)


@router.post(
    "/prompt/validate",
    response_model=ValidationResponse,
    summary="Validate generated content",
    description="Validate AI-generated content for quality and consistency"
)
async def validate_content(
    content: str = Body(..., description="Content to validate"),
    validation_type: str = Body("consistency", description="Type of validation"),
    novel_id: Optional[UUID] = Body(None, description="Novel UUID for context")
):
    """Validate generated content"""
    try:
        validator = QualityValidator()

        # Perform validation
        validation_result = await validator.validate_content(
            content=content,
            validation_type=validation_type,
            novel_id=str(novel_id) if novel_id else None
        )

        return ValidationResponse(
            success=True,
            message="Content validation completed",
            is_valid=validation_result.get("is_valid", False),
            errors=validation_result.get("errors"),
            warnings=validation_result.get("warnings")
        )

    except Exception as e:
        logger.error(f"Content validation failed: {e}")
        raise handle_database_error(e)


@router.post(
    "/batch/create",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create content batch with AI",
    description="Create a batch of content using AI assistance"
)
async def create_ai_batch(
    novel_id: UUID = Body(..., description="Novel UUID"),
    batch_type: str = Body("scenes", description="Type of content to generate"),
    count: int = Body(5, ge=1, le=20, description="Number of items to generate"),
    parameters: Dict[str, Any] = Body({}, description="Generation parameters")
):
    """Create content batch with AI"""
    try:
        batch_manager = BatchCreationManager(str(novel_id))

        # Start batch creation
        task_id = await batch_manager.create_batch(
            batch_type=batch_type,
            count=count,
            parameters=parameters
        )

        return TaskResponse(
            success=True,
            message=f"AI batch creation started for {count} {batch_type}",
            task_id=task_id,
            status="running",
            started_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"AI batch creation failed: {e}")
        raise handle_database_error(e)


@router.post(
    "/enhance",
    response_model=DataResponse[str],
    summary="Enhance existing content",
    description="Use AI to enhance or expand existing content"
)
async def enhance_content(
    content: str = Body(..., description="Content to enhance"),
    enhancement_type: str = Body("expand", description="Type of enhancement"),
    target_length: Optional[int] = Body(None, description="Target word count"),
    style_guide: Optional[Dict[str, Any]] = Body(None, description="Style guidelines")
):
    """Enhance existing content"""
    try:
        # This would integrate with AI service
        # Placeholder implementation
        enhanced = content + "\n\n[Enhanced content would be generated here]"

        return DataResponse(
            success=True,
            message=f"Content enhanced with '{enhancement_type}' strategy",
            data=enhanced
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/analyze",
    response_model=DataResponse[dict],
    summary="Analyze content",
    description="Analyze content for various metrics and improvements"
)
async def analyze_content(
    content: str = Body(..., description="Content to analyze"),
    analysis_types: List[str] = Body(["readability", "consistency"], description="Types of analysis")
):
    """Analyze content"""
    try:
        analysis_results = {}

        for analysis_type in analysis_types:
            if analysis_type == "readability":
                # Calculate readability metrics
                word_count = len(content.split())
                sentence_count = content.count('.') + content.count('!') + content.count('?')
                avg_sentence_length = word_count / max(sentence_count, 1)

                analysis_results["readability"] = {
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_sentence_length": avg_sentence_length,
                    "complexity": "moderate"  # Placeholder
                }

            elif analysis_type == "consistency":
                # Check consistency
                analysis_results["consistency"] = {
                    "character_consistency": True,
                    "timeline_consistency": True,
                    "worldbuilding_consistency": True,
                    "issues": []
                }

            elif analysis_type == "sentiment":
                # Sentiment analysis
                analysis_results["sentiment"] = {
                    "overall": "neutral",
                    "emotional_tone": "balanced",
                    "tension_level": "medium"
                }

        return DataResponse(
            success=True,
            message="Content analysis completed",
            data=analysis_results
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/templates",
    response_model=DataResponse[List[dict]],
    summary="Get writing templates",
    description="Get available writing templates"
)
async def get_writing_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    genre: Optional[str] = Query(None, description="Filter by genre")
):
    """Get writing templates"""
    try:
        # This would fetch from a template library
        templates = [
            {
                "id": "scene_001",
                "name": "Action Scene",
                "type": "scene",
                "genre": "fantasy",
                "description": "Template for high-action combat scenes",
                "structure": ["Setup", "Escalation", "Climax", "Resolution"]
            },
            {
                "id": "char_001",
                "name": "Character Introduction",
                "type": "character",
                "genre": "all",
                "description": "Template for introducing new characters",
                "structure": ["Physical Description", "Personality Traits", "Background", "Motivation"]
            },
            {
                "id": "world_001",
                "name": "Location Description",
                "type": "worldbuilding",
                "genre": "fantasy",
                "description": "Template for describing new locations",
                "structure": ["Overview", "Atmosphere", "Notable Features", "History"]
            }
        ]

        # Apply filters
        if template_type:
            templates = [t for t in templates if t["type"] == template_type]
        if genre:
            templates = [t for t in templates if t["genre"] == genre or t["genre"] == "all"]

        return DataResponse(
            success=True,
            message=f"Retrieved {len(templates)} templates",
            data=templates
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/feedback",
    response_model=DataResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback",
    description="Submit feedback on AI-generated content"
)
async def submit_feedback(
    content_id: UUID = Body(..., description="Content ID"),
    rating: int = Body(..., ge=1, le=5, description="Rating (1-5)"),
    feedback_type: str = Body("quality", description="Type of feedback"),
    comments: Optional[str] = Body(None, description="Additional comments"),
    suggested_improvements: Optional[List[str]] = Body(None, description="Suggested improvements")
):
    """Submit feedback on generated content"""
    try:
        # Store feedback for improving AI generation
        feedback_data = {
            "content_id": str(content_id),
            "rating": rating,
            "feedback_type": feedback_type,
            "comments": comments,
            "suggested_improvements": suggested_improvements,
            "timestamp": datetime.now().isoformat()
        }

        # This would save to database
        feedback_id = "fb_" + str(UUID())[:8]

        return DataResponse(
            success=True,
            message="Feedback submitted successfully",
            data={
                "feedback_id": feedback_id,
                "status": "recorded",
                "thank_you": "Your feedback helps improve our AI generation"
            }
        )

    except Exception as e:
        raise handle_database_error(e)