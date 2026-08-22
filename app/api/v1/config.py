from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.company import CompanyConfig
from app.schemas.company import CompanyConfigUpdate

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("")
async def get_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CompanyConfig).limit(1))
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company config not found")
    return model_to_dict(company)


@router.put("")
async def update_config(payload: CompanyConfigUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CompanyConfig).limit(1))
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company config not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    await db.flush()
    await db.refresh(company)
    return model_to_dict(company)
