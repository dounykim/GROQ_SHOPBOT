import streamlit as st
import comet_llm
from groq import Groq

# Comet API 키를 설정한다. st.secrets를 통해 안전하게 API 키를 불러온다.
COMET_API_KEY = st.secrets['COMET_API_KEY'] 
GROQ_API_KEY = st.secrets['GROQ_API_KEY'] 

# Groq Client 설정
client = Groq(api_key=GROQ_API_KEY)

# Comet LLM 초기화 및 프로젝트 이름을 설정
comet_llm.init(project='E-commerce_Chatbot', api_key=COMET_API_KEY)

# 제품 목록을 정의한다. 이 목록은 챗봇의 컨텍스트로 사용하며, 사용자가 대화 중에 요청할 수 있는 제품 정보를 포함한다.
product_list = '''
# 패션샵 제품 목록

## 남성 의류:
- 티셔츠
  - 가격: 20 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 그린, 화이트, 블랙, 그레이, 네이비

- 청바지
  - 가격: 50 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 블루, 블랙, 그레이, 네이비

## 여성 의류:
- 티셔츠
  - 가격: 20 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 레드, 화이트, 블랙, 그레이, 네이비

- 드레스
  - 가격: 50 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 레드, 화이트, 블랙, 그레이, 네이비
'''

# --- 챗봇의 System Message 설정 --------------------------------------------------
SYSTEM_MESSAGE = f'''
당신은 온라인 패션 상점 Trendy Fashion의 AI 어시스턴트인 ShopBot입니다.

당신의 역할은 고객을 응대하고, 고객이 원하는 제품을 찾도록 재고 목록을 참고하여 정보를 제공하며, 구매 과정을 안내하는 것입니다.

**반드시** 고객이 사용하는 언어에 맞춰서 응답해야 합니다. 만약 고객이 한국어로 메시지를 보냈다면, 반드시 한국어로 응답해야 합니다. 한국어와 영어 이외 다른 언어는 사용하지 마세요.

저희 상점에서는 현재 남성 의류와 여성 의류를 판매하고 있습니다.

전체 재고 목록은 다음과 같습니다:

```{product_list}```

**환영 인사는 처음 한 번만 합니다. 이미 고객에게 인사 메시지를 보여준 상태이므로, 고객이 '안녕하세요' 등으로 인사를 하더라도 똑같이 인사를 하지 말고, 바로 찾고 있는 제품이 있는지 물어보세요.**

고객의 메시지에는 항상 친절하게 답변해야 합니다.
'''

GREETINGS = '''반갑습니다, 고객님.

Trendy Fashion에 오신 것을 환영합니다. 

저는 이 상점의 AI 어시스턴트인 ShopBot입니다. 

어떤 상품을 찾고 계신가요? 

남성분들을 위한 👕티셔츠와 👖청바지, 여성분들을 위한 👚티셔츠와 👗드레스가 준비되어 있습니다.

궁금한 점이 있거나 도움이 필요하면 언제든지 저에게 알려주세요. 
'''

# 시스템 메시지와 인사말을 설정한다.
context = [
    {'role': 'system', 'content': SYSTEM_MESSAGE},
    {'role': 'assistant', 'content': GREETINGS}
]

# --- Streamlit 구성 -----------------------------------------------------------
# 메인 화면에 타이틀과 캡션을 설정한다.
st.title('🛍️ Trendy Fashion 🛍️')    # 웹 애플리케이션의 제목을 설정한다.
st.caption('🤖 AI 쇼핑 어시스턴트입니다.')       # 설명 문구(부제목)를 추가한다.

# 세션 상태에 'messages' 키가 없으면 빈 리스트로 초기화한다.
if 'messages' not in st.session_state:  
    st.session_state['messages'] = []
    # 인사 메시지를 세션 상태에 추가한다.
    st.session_state['messages'].append({'role': 'assistant', 'content': GREETINGS})

# 대화 기록을 화면에 출력한다.
for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

# 사용자 입력 처리 및 GPT 응답 생성
if prompt := st.chat_input():
    # 사용자 입력을 대화 기록에 추가
    st.session_state['messages'].append({'role': 'user', 'content': prompt})
    st.chat_message('user').write(prompt)

    # GPT 모델을 사용하여 응답 생성 (context를 메시지에 추가하여 사용)
    response = client.chat.completions.create(
        model='gemma2-9b-it',
        messages=context + st.session_state['messages']
    )
    
    # 응답 메시지를 대화 기록에 추가
    msg = response.choices[0].message.content
    st.session_state['messages'].append({'role': 'assistant', 'content': msg})
    st.chat_message('assistant').write(msg)

    # Comet LLM 로그 저장
    comet_llm.log_prompt(
        prompt=prompt,
        output=msg,
        metadata={
            'role': st.session_state['messages'][-1]['role'],
            'content': st.session_state['messages'][-1]['content'],
            'context': st.session_state['messages'],
            'product_list': product_list
        }
    )
