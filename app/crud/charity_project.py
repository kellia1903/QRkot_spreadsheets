from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_charity_project_by_name(
        self,
        charity_project_name: str,
        session: AsyncSession
    ):
        charity_project = await session.execute(
            select(self.model).where(self.model.name == charity_project_name)
        )
        return charity_project.scalars().first()
    
    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession()
    ):
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            ).order_by(
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date)
            )
        )
        
        return projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
