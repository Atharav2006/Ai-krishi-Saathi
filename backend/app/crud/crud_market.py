from typing import List, Tuple
from sqlalchemy.orm import Session
import uuid
from datetime import date
from app.crud.base import CRUDBase
from app.models.market import Market, MandiPrice
from app.schemas.market import MarketBase, MandiPriceBase

class CRUDMarket(CRUDBase[Market, MarketBase, MarketBase]):
    def get_by_district(self, db: Session, *, district_id: uuid.UUID) -> List[Market]:
        return db.query(Market).filter(Market.district_id == district_id).all()

class CRUDMandiPrice(CRUDBase[MandiPrice, MandiPriceBase, MandiPriceBase]):
    def get_paginated(
        self,
        db: Session,
        *,
        crop_id: uuid.UUID = None,
        district_id: uuid.UUID = None,
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[int, List[MandiPrice]]:
        """
        Calculates pagination alongside filtered timeseries values.
        """
        query = db.query(MandiPrice)
        
        if crop_id:
            query = query.filter(MandiPrice.crop_id == crop_id)
        if district_id:
            # Joining markets to filter prices strictly by localized districts
            query = query.join(Market).filter(Market.district_id == district_id)
        if start_date:
            query = query.filter(MandiPrice.price_date >= start_date)
        if end_date:
            query = query.filter(MandiPrice.price_date <= end_date)

        total_count = query.count()
        results = query.order_by(MandiPrice.price_date.desc()).offset(skip).limit(limit).all()
        return total_count, results

market = CRUDMarket(Market)
mandi_price = CRUDMandiPrice(MandiPrice)
