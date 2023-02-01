from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.schemas import (CharityProjectBase, CharityProjectDB, CharityProjectUpdate)
from app.services.investments import allocate_donation_funds

from ..validators import (check_charity_project_before_delete,
                          check_charity_project_before_update,
                          check_charity_project_name_duplilcate)


router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    return await charity_project_crud.get_multi(session=session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectBase,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    await check_charity_project_name_duplilcate(
        charity_project_name=charity_project.name,
        session=session
    )
    new_charity_project = await charity_project_crud.create(
        obj_in=charity_project, session=session
    )
    await allocate_donation_funds(session=session)
    await session.refresh(new_charity_project)
    return new_charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_before_delete(
        charity_project_id=project_id, session=session
    )
    deleted_charity_project = await charity_project_crud.delete(
        db_obj=charity_project, session=session
    )
    return deleted_charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    charity_project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project_db = await check_charity_project_before_update(
        charity_project_id=project_id,
        session=session,
        charity_project_in=charity_project_in
    )
    charity_project = await charity_project_crud.update(
        db_obj=charity_project_db, obj_in=charity_project_in, session=session
    )
    return charity_project
