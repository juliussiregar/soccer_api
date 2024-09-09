from datetime import date
import json
import pandas as pd
from sqlalchemy import func
from app.core.constants.app import DEFAULT_TZ
from app.core.database import get_session
from app.models.actuals import Actual, SubActual
from app.repositories.actual import ActualRepository
from app.schemas.actual_mgt import SubActualUpdate
from app.schemas.food_mgt import FoodFilter, FoodInsert
from app.utils.calculate_formulas import DetailCalculate

class ActualRepository:
    def get_date (self, user_id : int) -> Actual:
        with get_session() as db:
            actuals = db.query(Actual)
            date = actuals.filter(Actual.userid == user_id).one_or_none()
            return date
    def test (self):
        date = self.get_date(5)
        print (date.created_at)
        

def testing ():
    actual = ActualRepository()
    actual.test()

testing()



