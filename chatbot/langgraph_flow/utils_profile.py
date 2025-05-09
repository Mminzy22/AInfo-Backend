from datetime import date
from accounts.models import User
from channels.db import database_sync_to_async

# interests: ManyToManyField -> 문자열로 변환
@database_sync_to_async
def get_interest(user: User) -> str:
    interests = user.interests.all()
    return ", ".join(i.name for i in interests) if interests else ""

# education_level: ForeignKey -> 문자열
@database_sync_to_async
def get_education(user: User) -> str:
    return user.education_level.name if user.education_level else ""

# current_status: ForeignKey -> 문자열
@database_sync_to_async
def get_job_status(user: User) -> str:
    return user.current_status.name if user.current_status else ""

# location: ForeignKey (Region + SubRegion) -> 문자열
@database_sync_to_async
def get_location(user: User) -> str:
    if not user.location:
        return ""
    region_name = user.location.region.name if user.location.region else ""
    subregion_name = user.location.name
    return f"{region_name} - {subregion_name}" if region_name else subregion_name

# 나이: birth_date -> 현재 날짜 기준으로 만 나이 계산
@database_sync_to_async
def get_age(user: User) -> str:
    if not user.birth_date:
        return ""
    today = date.today()
    born = user.birth_date
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return str(age)