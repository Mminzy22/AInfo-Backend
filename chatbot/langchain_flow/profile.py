from channels.db import database_sync_to_async

from accounts.models import User


@database_sync_to_async
def get_profile_data(user_id: int) -> dict:
    """
    주어진 사용자 ID에 해당하는 사용자의 프로필 정보를 비동기적으로 조회하여
    키워드 목록과 프로필 딕셔너리를 반환합니다.

    이 함수는 Django ORM을 사용하여 User 객체 및 연관된 모델 정보
    (학력, 현재 상태, 관심사, 거주지 등)를 조회하고, 이를 기반으로
    정책 추천 등에 사용할 수 있는 키워드 리스트와 정형화된 프로필 데이터를 생성합니다.

    Args:
        user_id (int): 조회할 사용자의 기본 키(ID).

    Returns:
        dict: 다음과 같은 구조의 딕셔너리를 반환합니다.
            {
                "keywords": List[str],
                "profile": {
                    "interests": List[str],
                    "education_level": str,
                    "current_status": str,
                    "location": str,
                    "region": str
                }
            }
    """
    user = User.objects.get(pk=user_id)

    education_level = user.education_level
    current_status = user.current_status
    location = user.location
    region = location.region if location else None

    interests = user.interests.all()
    interest_list = [interest.name for interest in interests]

    keywords = []
    profile = {}

    keywords += interest_list
    profile["interests"] = interest_list

    if education_level:
        keywords.append(education_level.name)
        profile["education_level"] = education_level.name

    if current_status:
        keywords.append(current_status.name)
        profile["current_status"] = current_status.name

    if location:
        keywords.append(location.name)
        profile["location"] = location.name

    if region:
        keywords.append(region.name)
        profile["region"] = region.name

    return {"keywords": keywords, "profile": profile}
