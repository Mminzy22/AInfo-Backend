from langchain.prompts import PromptTemplate

FINAL_ANSWER_PROMPT = PromptTemplate.from_template(
    """
    너는 테스트용 챗봇이야.
    
    user_message : {user_message}
    이런질문을 받으면 
    아래 정보를 바탕으로 적절한 답변을 해야해
    
    chat_history : {chat_history}
    is_relevant : {is_relevant}
    interest : {interest}
    education : {education}
    job_status : {job_status}
    location : {location}
    age : {age}
    retrieved_docs : {retrieved_docs}
    web_docs : {web_docs}
    web_search_query : {web_search_query}
    final_context : {final_context}
    search_retry_count : {search_retry_count}
    
    그런데 지금은 테스트용으로 만들고있어 그러니까 내가 받아온 정보가 정확한건지 확인하기위해 저 정보들을 그대로 답변해줘
    
    답변 양식은 아래와같아 
    user_message :
    chat_history : 
    is_relevant : 
    interest : 
    education : 
    job_status : 
    location : 
    age: 
    retrieved_docs : 
    web_docs : 
    web_search_query : 
    final_context : 
    search_retry_count :
    """
)