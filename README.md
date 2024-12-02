# Facetes AI Agent

개인화된 다중 특성(Multi-Faceted) 기반의 지능형 대화 에이전트 시스템

## 프로젝트 개요

이 프로젝트는 사용자의 다양한 특성(Facets)을 학습하고 활용하여 개인화된 대화를 제공하는 AI 에이전트 시스템입니다. 활동 패턴, 행동 특성, 관심사, 상호작용 이력 등 다차원적인 사용자 특성을 분석하여 맥락에 맞는 자연스러운 대화를 실현합니다.

## 핵심 특징

- **다중 특성 기반 개인화**
  - 활동/행동 패턴 분석
  - 관심사 및 선호도 학습
  - 상호작용 패턴 추적
  
- **컨텍스트 인식 대화**
  - 실시간 대화 문맥 분석
  - 시공간 컨텍스트 처리
  - 장단기 메모리 관리

- **지능형 응답 생성**
  - 개인화된 응답 생성
  - 상황 적응형 프롬프트
  - 품질 관리 및 최적화

## 시스템 아키텍처

### 핵심 모듈 구성

**1. Analyzers (분석 엔진)**
```
analyzers/
├── context_prioritizer.py    # 컨텍스트 우선순위 처리
├── context_processor.py      # 컨텍스트 분석 및 처리
├── conversation_analyzer.py  # 대화 분석 메인 엔진
├── conversation_flow_manager.py  # 대화 흐름 관리
└── similarity_analyzer.py    # 대화 유사도 분석
```

**2. Facets (사용자 특성 관리)**
```
facets/
├── activity_facet.py        # 활동 정보 관리
├── behavior_facet.py        # 행동 패턴 분석
├── context_memory.py        # 컨텍스트 메모리
├── interaction_metrics.py   # 상호작용 지표
├── knowledge_base.py        # 지식 베이스
├── user_interests.py        # 관심사 관리
└── user_profile.py          # 사용자 프로필
```

**3. Generators (생성 엔진)**
```
generators/
├── prompt_generator.py      # 프롬프트 생성
└── response_generator.py    # 응답 생성
```

### 모듈별 상세 설명

#### Analyzers 모듈

Analyzers 모듈은 대화 분석의 핵심 기능을 담당하며, 다섯 가지 주요 컴포넌트로 구성됩니다.
ContextPrioritizer는 대화의 시간적 맥락과 유형별 중요도를 관리합니다. 최근 대화에는 0.6, 당일 대화에는 0.3, 이전 대화에는 0.1의 가중치를 부여하며, 위치(0.4), 시간(0.3), 주제(0.2), 의도(0.1)와 같은 유형별 가중치를 적용하여 컨텍스트의 우선순위를 결정합니다.
ContextProcessor는 대화에서 위치, 시간, 주제, 의도 등의 컨텍스트 정보를 추출하고 분석합니다. 추출된 정보의 신뢰도를 평가하고, 적절한 가중치를 적용하여 처리합니다.
ConversationAnalyzer는 OpenAI API를 활용하여 대화를 분석하고 구조화합니다. 사용자의 입력을 분석하여 의미를 파악하고, 컨텍스트를 기반으로 적절한 응답을 생성하며, 사용자 프로필을 지속적으로 업데이트합니다.
ConversationFlowManager는 대화의 흐름을 관리합니다. 현재 대화 상태를 추적하고, 사용자의 의도가 명확하지 않을 때 추가 명확화가 필요한지 판단하며, 컨텍스트 스택을 통해 대화의 맥락을 유지합니다.
SimilarityAnalyzer는 대화 간의 유사성을 분석합니다. 키워드 기반의 유사도 분석, 시간에 따른 필터링, 그리고 LLM을 활용한 의미적 유사도 계산을 수행합니다.

#### Facets 모듈

Facets 모듈은 사용자의 다양한 특성과 행동을 관리하는 일곱 가지 컴포넌트로 구성됩니다.
ActivityFacet은 사용자의 활동을 기록하고 분석하며, 활동 패턴을 추적하여 통계를 생성합니다. BehaviorFacet은 사용자의 행동 패턴을 분석하고 선호도를 학습하여 향후 행동을 예측하는 모델을 구축합니다.
ContextMemory는 대화의 단기 및 장기 메모리를 관리하며, 컨텍스트의 효율적인 저장과 검색을 담당합니다. InteractionMetrics는 대화의 참여도를 측정하고 응답의 품질을 평가하며 상호작용 패턴을 분석합니다.
KnowledgeBase는 도메인별 지식을 관리하고 정보를 검색하며 지식 그래프를 구축합니다. UserInterests는 사용자의 관심사 프로필을 관리하고 선호도 점수를 계산하며 관심사의 변화를 추적합니다.
UserProfile은 사용자의 통합 프로필을 관리하고 실시간으로 업데이트하며 개인화된 설정을 관리합니다.

#### Generators 모듈

Generators 모듈은 두 가지 주요 컴포넌트로 구성됩니다.
PromptGenerator는 상황에 맞는 프롬프트 템플릿을 관리하고 동적으로 프롬프트를 생성하며 최적화합니다. ResponseGenerator는 컨텍스트를 기반으로 응답을 생성하고 품질을 관리하며 적절한 형식으로 포맷팅합니다.

#### Utils 모듈

Utils 모듈은 시스템의 기반 기능을 제공하는 네 가지 컴포넌트로 구성됩니다.
Constants는 시스템에서 사용되는 상수들을 정의하고 설정값을 관리합니다. DomainMapper는 도메인을 분류하고 토픽과 도메인 간의 변환을 담당합니다.
Logger는 시스템의 로깅 기능을 제공하고 디버그 정보를 관리합니다. TextParser는 텍스트를 분석하고 파싱하며 LLM의 응답을 처리합니다.

### 시스템 아키텍처 다이어그램
<img width="1690" alt="image" src="https://github.com/user-attachments/assets/560b7634-72a3-4985-957a-b2f14cefe16f">

## 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/username/facetes-ai-agent.git

# 환경 설정
conda create -n facetes python=3.11
conda activate facetes

# 의존성 설치
pip install -r requirements.txt

# 실행
python src/main.py
```

**의존성 상세 명시**
```text
requirements.txt
---------------
openai>=1.0.0
asyncio>=3.4.3
gradio>=4.0.0
numpy>=1.21.0
```

**환경 변수 설정**
```bash
# .env 파일 설정
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
```

## 기술 스택

- Python 3.11
- OpenAI GPT-4
- AsyncIO
- Gradio UI

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Type Hints 사용
- Docstring 필수

### 테스트
- 단위 테스트 필수
- 통합 테스트 권장
- 80% 이상 커버리지

### 문서화
- API 문서 작성
- 예제 코드 제공
- 변경 이력 관리

## 라이선스

MIT License
