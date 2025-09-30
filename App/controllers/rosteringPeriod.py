from App.database import db
from App.models import RosteringPeriod # Imports the model you confirmed
from datetime import date
from sqlalchemy.exc import IntegrityError

def create_rostering_period(start_date: date, end_date: date):
    """
    Admin function to define the start and end dates for a new weekly roster period.
    """
    # 1. Validation: Ensure start date is before end date
    if start_date >= end_date:
        return {"error": "Start date must be before end date."}
        
    new_period = RosteringPeriod(
        startDate=start_date,
        endDate=end_date
    )
    
    try:
        db.session.add(new_period)
        db.session.commit()
        return {
            "message": f"New roster period created from {start_date.isoformat()} to {end_date.isoformat()}.", 
            "id": new_period.id
        }
    except IntegrityError:
        # This handles the UniqueConstraint if the same period is added twice
        db.session.rollback()
        return {"error": "A rostering period with these dates already exists."}
    except Exception as e:
        db.session.rollback()
        return {"error": f"Database error: {str(e)}"}
