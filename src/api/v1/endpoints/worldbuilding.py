"""
Worldbuilding Management Endpoints
Handles domains, law chains, and characters
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body, Path, status

from database.models.worldbuilding_models import (
    Domain, DomainCreate, DomainType,
    LawChain, LawChainCreate, ItemRarity
)
from database.models.character_models import Character
from database.models.content_models import CharacterCreate
from api.v1.schemas.responses import DataResponse, ListResponse
from api.core.database import get_novel_data_manager, get_law_chain_mgr
from api.core.exceptions import NotFoundException, ConflictException, handle_database_error
from database.data_access import DatabaseError

router = APIRouter()


# Domain endpoints
@router.post(
    "/domains",
    response_model=DataResponse[Domain],
    status_code=status.HTTP_201_CREATED,
    summary="Create domain",
    description="Create a new domain in the Nine Domains system"
)
async def create_domain(
    domain: DomainCreate = Body(..., description="Domain details")
):
    """Create a new domain"""
    try:
        novel_manager = get_novel_data_manager(str(domain.novel_id))
        created_domain = await novel_manager.create_domain(domain)

        return DataResponse(
            success=True,
            message=f"Domain '{created_domain.name}' created successfully",
            data=created_domain
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/domains",
    response_model=ListResponse[Domain],
    summary="List domains",
    description="List all domains for a novel"
)
async def list_domains(
    novel_id: UUID = Query(..., description="Novel UUID"),
    domain_type: Optional[DomainType] = Query(None, description="Filter by domain type"),
    min_power: Optional[int] = Query(None, ge=1, le=10, description="Minimum power level")
):
    """List domains for a novel"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))
        domains = await novel_manager.get_domains()

        # Apply filters
        if domain_type:
            domains = [d for d in domains if d.domain_type == domain_type]
        if min_power:
            domains = [d for d in domains if d.power_level >= min_power]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(domains)} domains",
            data=domains,
            total=len(domains)
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/domains/{domain_id}",
    response_model=DataResponse[Domain],
    summary="Get domain by ID",
    description="Get detailed information about a specific domain"
)
async def get_domain(
    domain_id: UUID = Path(..., description="Domain UUID"),
    include_law_chains: bool = Query(False, description="Include associated law chains")
):
    """Get a specific domain"""
    try:
        # This would need implementation
        domain = await get_domain_by_id(domain_id)
        if not domain:
            raise NotFoundException("Domain", str(domain_id))

        if include_law_chains:
            # Get associated law chains
            pass

        return DataResponse(
            success=True,
            message="Domain retrieved successfully",
            data=domain
        )

    except DatabaseError as e:
        raise handle_database_error(e)


# Law Chain endpoints
@router.post(
    "/law-chains",
    response_model=DataResponse[LawChain],
    status_code=status.HTTP_201_CREATED,
    summary="Create law chain",
    description="Create a new law chain"
)
async def create_law_chain(
    law_chain: LawChainCreate = Body(..., description="Law chain details")
):
    """Create a new law chain"""
    try:
        novel_manager = get_novel_data_manager(str(law_chain.novel_id))
        created_chain = await novel_manager.create_law_chain(law_chain)

        return DataResponse(
            success=True,
            message=f"Law chain '{created_chain.name}' created successfully",
            data=created_chain
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/law-chains",
    response_model=ListResponse[LawChain],
    summary="List law chains",
    description="List all law chains for a novel"
)
async def list_law_chains(
    novel_id: UUID = Query(..., description="Novel UUID"),
    chain_type: Optional[str] = Query(None, description="Filter by chain type"),
    rarity: Optional[ItemRarity] = Query(None, description="Filter by rarity"),
    min_power: Optional[int] = Query(None, ge=1, le=10, description="Minimum power level")
):
    """List law chains for a novel"""
    try:
        law_chain_manager = await get_law_chain_mgr()
        chains = await law_chain_manager.get_law_chains(str(novel_id))

        # Apply filters
        if chain_type:
            chains = [c for c in chains if c.chain_type == chain_type]
        if rarity:
            chains = [c for c in chains if c.rarity == rarity]
        if min_power:
            chains = [c for c in chains if c.power_level >= min_power]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(chains)} law chains",
            data=chains,
            total=len(chains)
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/law-chains/{chain_id}",
    response_model=DataResponse[LawChain],
    summary="Get law chain by ID",
    description="Get detailed information about a specific law chain"
)
async def get_law_chain(
    chain_id: UUID = Path(..., description="Law chain UUID")
):
    """Get a specific law chain"""
    try:
        law_chain_manager = await get_law_chain_mgr()
        chain = await law_chain_manager.get_law_chain(str(chain_id))

        if not chain:
            raise NotFoundException("Law chain", str(chain_id))

        return DataResponse(
            success=True,
            message="Law chain retrieved successfully",
            data=chain
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.post(
    "/law-chains/analyze",
    response_model=DataResponse[dict],
    summary="Analyze law chains",
    description="Analyze law chain relationships and conflicts"
)
async def analyze_law_chains(
    novel_id: UUID = Body(..., description="Novel UUID"),
    domain_filter: Optional[str] = Body(None, description="Filter by domain")
):
    """Analyze law chain relationships"""
    try:
        law_chain_manager = await get_law_chain_mgr()
        analysis = await law_chain_manager.analyze_law_chains(
            str(novel_id),
            domain_filter=domain_filter
        )

        return DataResponse(
            success=True,
            message="Law chain analysis completed",
            data=analysis
        )

    except DatabaseError as e:
        raise handle_database_error(e)


# Character endpoints
@router.post(
    "/characters",
    response_model=DataResponse[Character],
    status_code=status.HTTP_201_CREATED,
    summary="Create character",
    description="Create a new character"
)
async def create_character(
    character: CharacterCreate = Body(..., description="Character details")
):
    """Create a new character"""
    try:
        novel_manager = get_novel_data_manager(character.novel_id)
        created_character = await novel_manager.create_character(character)

        return DataResponse(
            success=True,
            message=f"Character '{created_character.name}' created successfully",
            data=created_character
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/characters",
    response_model=ListResponse[Character],
    summary="List characters",
    description="List all characters for a novel"
)
async def list_characters(
    novel_id: UUID = Query(..., description="Novel UUID"),
    character_type: Optional[str] = Query(None, description="Filter by character type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List characters for a novel"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))
        characters = await novel_manager.get_characters()

        # Apply filters
        if character_type:
            characters = [c for c in characters if c.character_type == character_type]
        if tags:
            characters = [c for c in characters if any(tag in c.tags for tag in tags)]

        # Apply pagination
        total = len(characters)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_characters = characters[start:end]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(paginated_characters)} characters",
            data=paginated_characters,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/characters/{character_id}",
    response_model=DataResponse[Character],
    summary="Get character by ID",
    description="Get detailed information about a specific character"
)
async def get_character(
    character_id: str = Path(..., description="Character ID"),
    include_relationships: bool = Query(False, description="Include character relationships")
):
    """Get a specific character"""
    try:
        # This would need implementation
        character = await get_character_by_id(character_id)
        if not character:
            raise NotFoundException("Character", character_id)

        if include_relationships:
            # Get character relationships
            pass

        return DataResponse(
            success=True,
            message="Character retrieved successfully",
            data=character
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.patch(
    "/characters/{character_id}",
    response_model=DataResponse[Character],
    summary="Update character",
    description="Update character information"
)
async def update_character(
    character_id: str = Path(..., description="Character ID"),
    update_data: dict = Body(..., description="Fields to update")
):
    """Update a character"""
    try:
        # This would need implementation
        character = await update_character_data(character_id, update_data)
        if not character:
            raise NotFoundException("Character", character_id)

        return DataResponse(
            success=True,
            message="Character updated successfully",
            data=character
        )

    except DatabaseError as e:
        raise handle_database_error(e)


# Helper functions (placeholders - need implementation)
async def get_domain_by_id(domain_id: UUID):
    """Get domain by ID - placeholder"""
    pass

async def get_character_by_id(character_id: str):
    """Get character by ID - placeholder"""
    pass

async def update_character_data(character_id: str, update_data: dict):
    """Update character - placeholder"""
    pass