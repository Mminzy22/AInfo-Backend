from langchain.prompts import PromptTemplate

RELEVANCE_CHECK_PROMPT = PromptTemplate.from_template(
    """
    당신은 RAG 검색으로 나온 문서(지원정책, 제도)가 사용자의 정보에 부합하는지 판단하는 시스템입니다.
    
    당신의 임무는 다음과 같습니다:
    1. 사용자의 정보가 정책,제도 의 제한사항에 부합하는지 판단한다.
        - 제한사항은 지원자격, 자격요건, 시행일자, 지원기간 등을 포함한다.
        - 부합하지 않다면 해당 내용은 문서에서 제외시킨다.
        - 사용자의 정보가 비어있거나, 문서에서 제한사항이 없다면 부합하는것으로 판단한다.
        - 문서들은 구분선(---)으로 구분되어있으며 제외할시 가능한 원본내용은 유지한다.
    3. 최종 문서의 갯수가 5개이하라면 web_search 의 값을 "Y" 로 반환한다.
        - 6개이상이라면 "N" 으로 반환한다.
    
    [사용자 정보]
    학력: {education}
    직업상태: {job_status}
    거주지: {location}
    나이: {age}
    현재날짜: {current_year}
    
    [문서 내용]
    {docs}
    
    ##답변 형식
    다음과 같은 JSON 형식으로 결과를 반환하십시오:
        "retrieved_docs": "string",
        "web_search": "Y" or "N"
    """
)