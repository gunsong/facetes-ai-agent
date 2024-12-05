import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from utils.constants import Domain
from utils.domain_mapper import DomainMapper
from utils.logger import get_logger

from .activity_facet import Activities
from .behavior_facet import BehaviorPatterns
from .context_memory import ContextMemory
from .interaction_metrics import InteractionMetrics
from .knowledge_base import KnowledgeBase
from .user_interests import UserInterests

logger = get_logger(__name__)

class UserProfile:
    def __init__(self):
        """사용자 프로필 초기화"""
        logger.info("UserProfile 초기화 시작")

        # 각 컴포넌트 클래스 인스턴스화
        self.interests = UserInterests()  # 관심사 객체 초기화
        self.activities = Activities()    # 활동 정보
        self.behavior = BehaviorPatterns() # 행동 패턴
        self.context = ContextMemory()    # 컨텍스트 메모리
        self.metrics = InteractionMetrics() # 상호작용 지표
        self.knowledge = KnowledgeBase()  # 지식 베이스

        # 프로필 메타데이터
        self.last_update = None
        self.profile_version = "1.0.0"

        # 프로필 데이터 구조 초기화
        self.profile = self._initialize_profile()

        logger.info("UserProfile 초기화 완료")

    def _initialize_profile(self) -> Dict:
        """프로필 초기화"""
        return {
            "user_profile": {
                "personal_info": {
                    "name": "홍길동",  # 기본값 설정
                    "email": "user@example.com",  # 기본값 설정
                    "address": "서울시 강남구",  # 기본값 설정
                    "birth_date": None,
                    "nationality": None,
                    "language": [],
                    "age": None,
                    "gender": None,
                    "marital_status": None,
                    "phone": None,
                    "profile_image": None
                },
                "family_info": {
                    "family_members": [],  # [{"relation": "spouse", "age": 35}, ...]
                    "household_size": None,
                    "dependents": [],
                    "living_arrangement": None
                },
                "professional_info": {
                    "occupation": None,
                    "company_name": None,
                    "industry": None,
                    "position": None,
                    "work_address": None,
                    "work_hours": None,
                    "employment_history": [],
                    "skills": [],
                    "certifications": []
                },
                "residence_info": {
                    "current_address": None,
                    "housing_type": None,
                    "ownership_status": None,
                    "residence_period": None,
                    "previous_addresses": [],
                    "neighborhood": None,
                    "commute_preferences": {}
                }
            },
            "user_interests": {
                "topics": {},          # 관심 주제 분포
                "keywords": {},        # 자주 사용하는 키워드
                "entities": {},        # 언급된 고유 명사
                "preferences": {
                    "topics": {},      # 주제별 선호도
                    "activities": {},  # 활동 선호도
                    "locations": {},   # 장소 선호도
                    "food": {},        # 음식 선호도
                    "accommodation": {},# 숙박 선호도
                    "transportation": {},# 교통수단 선호도
                    "entertainment": {},# 엔터테인먼트 선호도
                    "shopping": {}     # 쇼핑 선호도
                }
            },
            "behavior_patterns": {
                "temporal": {          # 시간 관련 패턴
                    "daily": {},       # 하루 중 선호 시간
                    "weekly": {},      # 주간 선호 패턴
                    "monthly": {},     # 월간 패턴
                    "seasonal": {},    # 계절별 선호도
                    "periodic": {}     # 주기적 패턴
                },
                "spatial": {           # 공간 패턴
                    "locations": {},   # 선호 장소
                    "regions": {},     # 선호 지역
                    "venue_types": {}, # 선호 시설 유형
                    "types": {}        # 장소 유형
                },
                "social": {            # 사회적 패턴
                    "companions": {},  # 동반자 유형
                    "group_size": {},  # 선호 그룹 크기
                    "social_context": {},# 사회적 상황
                    "contexts": {}     # 상황별 패턴
                },
                "spending": {          # 소비 패턴
                    "amount_range": {},# 소비 금액대
                    "frequency": {},   # 소비 빈도
                    "categories": {}   # 소비 카테고리
                },
                "interaction_style": { # 상호작용 스타일
                    "query_types": {}, # 질문 유형 분포
                    "tone": {},        # 대화 톤 분포
                    "detail_level": {} # 상세도 선호도
                }
            },
            "knowledge_base": {
                "domains": {           # 도메인별 지식
                    "travel": {        # 여행 관련
                        "locations": {},
                        "preferences": {},
                        "frequency": {},
                        "style": {},
                        "history": {},
                        "plans": {}
                    },
                    "work": {          # 업무 관련
                        "field": {},
                        "style": {},
                        "schedule": {},
                        "preferences": {},
                        "skills": {},
                        "projects": {}
                    },
                    "hobby": {         # 취미 활동
                        "types": {},
                        "frequency": {},
                        "skill_level": {},
                        "preferences": {}
                    },
                    "learning": {      # 학습
                        "subjects": {},
                        "progress": {},
                        "goals": {}
                    },
                    "entertainment": { # 엔터테인먼트
                        "genres": {},
                        "venues": {},
                        "frequency": {}
                    },
                    "dining": {        # 음식/식당
                        "cuisines": {},
                        "occasions": {},
                        "preferences": {}
                    }
                },
                "connections": {},     # 도메인 간 연결 정보
                "cross_domain_patterns": {}, # 도메인 간 패턴
                "context_awareness": {} # 상황 인식
            },
            "activities": {
                "planned": [],         # 예정된 활동
                "completed": [],       # 완료된 활동
                "recurring": {         # 반복 활동
                    "daily": [],       # 일간 반복
                    "weekly": [],      # 주간 반복
                    "monthly": [],     # 월간 반복
                    "seasonal": []     # 계절별 반복
                },
                "interests": [],       # 관심 활동
                "patterns": {          # 활동 패턴
                    "frequency": {},   # 빈도
                    "combinations": {},# 조합
                    "sequences": {}    # 순서
                },
                "history": {           # 활동 이력
                    "by_category": {}, # 카테고리별
                    "by_location": {}, # 위치별
                    "by_companion": {} # 동반자별
                }
            },
            "context_memory": {
                "short_term": [],      # 최근 대화 컨텍스트
                "long_term": {         # 장기 기억
                    "preferences": {}, # 누적된 선호도
                    "experiences": {}, # 과거 경험
                    "decisions": {},   # 과거 결정들
                    "patterns": {}     # 장기 패턴
                }
            },
            "interaction_metrics": {
                "counts": {
                    "total": 0,        # 전체 상호작용 수
                    "by_type": {},     # 유형별 상호작용
                    "by_domain": {}    # 도메인별 상호작용
                },
                "sentiment": {
                    "average": 0,      # 평균 감정 점수
                    "history": [],     # 감정 이력
                    "by_context": {}   # 상황별 감정
                },
                "engagement": {
                    "level": 0,        # 참여도 레벨
                    "trends": [],      # 참여 트렌드
                    "peaks": {}        # 최고 참여 시점
                },
                "query_history": [],   # 질의 이력
                "response_feedback": {},# 응답 피드백
                "satisfaction_scores": {} # 만족도 점수
            }
        }

    def update_from_analysis(self, analysis: Dict) -> None:
        """분석 결과로 프로필 업데이트"""
        try:
            if not analysis:
                return

            self.last_update = datetime.now()

            # 메인 토픽 업데이트
            main_topic = analysis.get("main_topic")
            if main_topic and main_topic != "unknown":
                self.interests.add_main_interest(main_topic)

            # 서브 토픽 업데이트
            sub_topics = analysis.get("sub_topics", {})
            for category, items in sub_topics.items():
                if items:
                    for item in items:
                        self.interests.add_sub_interest(category, item)

            # 개인 정보 업데이트
            personal_info = analysis.get("personal_info")
            logger.info(f"개인 정보 업데이트 시작: {personal_info}")
            if personal_info:
                self._update_personal_info(personal_info)
            logger.info(f"개인 정보 업데이트 완료: {main_topic}")

            # 활동 업데이트
            self.activities.update_activity_records(
                analysis,
                self.last_update.isoformat()
            )

            # 행동 패턴 업데이트
            self.behavior.update_patterns(analysis)

            # 컨텍스트 메모리 업데이트
            self.context.update_context_memory(analysis)

            # 관련 컨텍스트 검색
            relevant_context = self.context.get_relevant_context(analysis)

            # 컨텍스트를 고려한 분석 결과 업데이트
            if relevant_context:
                analysis = self._merge_with_context(analysis, relevant_context)

            # 상호작용 지표 업데이트
            self.metrics.update_metrics(analysis)

            # 지식 베이스 업데이트
            domain = self._map_domain(analysis.get("main_topic", "unknown"))
            self.knowledge.update_domain_knowledge(domain, analysis)

            logger.info(f"프로필 업데이트 완료: {main_topic}")
        except Exception as e:
            logger.error(f"프로필 업데이트 중 오류: {str(e)}")

    def update_default_personal_info(self, name: str = None, email: str = None, address: str = None) -> None:
        """개인 기본 정보 업데이트"""
        try:
            if name:
                self.profile["user_profile"]["personal_info"]["name"] = name
            if email:
                self.profile["user_profile"]["personal_info"]["email"] = email
            if address:
                self.profile["user_profile"]["personal_info"]["address"] = address

            logger.info(f"개인 기본 정보 업데이트 완료. {name}, {email}, {address}")
        except Exception as e:
            logger.error(f"개인 기본 정보 업데이트 중 오류: {str(e)}")

    def _update_personal_info(self, personal_info: Dict) -> None:
        """개인 정보 업데이트"""
        try:
            for info_type, info_data in personal_info.items():
                # 신뢰도 확인 및 로깅
                confidence = info_data.get("추출_신뢰도", 0)
                logger.info(f"처리 중인 정보 유형: {info_type}, 신뢰도: {confidence}")
                if confidence < 70:
                    logger.warning(f"낮은 신뢰도 정보 처리: {info_type} ({confidence})")

                if info_type == "기본 정보":
                    self._update_basic_info_if_exists(info_data)
                elif info_type == "가족 관계":
                    self._update_family_info_if_exists(info_data)
                elif info_type == "직업 정보":
                    self._update_professional_info_if_exists(info_data)
                elif info_type == "거주 정보":
                    self._update_residence_info_if_exists(info_data)
                else:
                    logger.warning(f"알 수 없는 정보 유형: {info_type}")

            logger.info("개인 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"개인 정보 업데이트 중 오류: {str(e)}")

    def _update_basic_info_if_exists(self, basic_info: Dict) -> None:
        """기본 정보 업데이트 (값이 있는 경우만)"""
        try:
            for key, value in basic_info.items():
                if value is not None and key in ["나이", "성별", "결혼상태"]:
                    self.profile["user_profile"]["personal_info"][key] = value
            logger.info("기본 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"기본 정보 업데이트 중 오류: {str(e)}")

    def _update_family_info_if_exists(self, family_info: Dict) -> None:
        """가족 관계 정보 업데이트 (값이 있는 경우만)"""
        try:
            family_data = self.profile["user_profile"]["family_info"]

            if members := family_info.get("구성원"):
                family_data["family_members"] = members

            if size := family_info.get("가구_크기"):
                family_data["household_size"] = size

            if arrangement := family_info.get("동거_여부"):
                family_data["living_arrangement"] = arrangement

            logger.info("가족 관계 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"가족 관계 정보 업데이트 중 오류: {str(e)}")

    def _update_professional_info_if_exists(self, job_info: Dict) -> None:
        """직업 정보 업데이트 (값이 있는 경우만)"""
        try:
            prof_data = self.profile["user_profile"]["professional_info"]

            if workplace := job_info.get("직장", {}):
                if company := workplace.get("회사명"):
                    prof_data["company_name"] = company
                if industry := workplace.get("업종"):
                    prof_data["industry"] = industry
                if location := workplace.get("근무지"):
                    prof_data["work_address"] = location

            if job_role := job_info.get("직무", {}):
                if position := job_role.get("직위"):
                    prof_data["position"] = position
                if role := job_role.get("역할"):
                    prof_data["occupation"] = role

            if work_type := job_info.get("근무형태"):
                prof_data["work_hours"] = work_type

            logger.info("직업 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"직업 정보 업데이트 중 오류: {str(e)}")

    def _update_residence_info_if_exists(self, residence_info: Dict) -> None:
        """거주 정보 업데이트 (값이 있는 경우만)"""
        try:
            res_data = self.profile["user_profile"]["residence_info"]

            if address := residence_info.get("주소"):
                current_address = " ".join(filter(None, [
                    address.get("도시"),
                    address.get("동네"),
                    address.get("상세주소")
                ]))
                if current_address:
                    res_data["current_address"] = current_address

            if housing := residence_info.get("주거형태"):
                res_data["housing_type"] = housing

            if ownership := residence_info.get("점유형태"):
                res_data["ownership_status"] = ownership

            if period := residence_info.get("거주기간"):
                res_data["residence_period"] = period

            logger.info("거주 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"거주 정보 업데이트 중 오류: {str(e)}")

    def _update_basic_info(self, basic_info: Dict) -> None:
        """기본 정보 업데이트"""
        try:
            self.profile["user_profile"]["personal_info"].update({
                "age": basic_info.get("나이"),
                "gender": basic_info.get("성별"),
                "marital_status": basic_info.get("결혼상태")
            })
        except Exception as e:
            logger.error(f"기본 정보 업데이트 중 오류: {str(e)}")

    def _update_family_info(self, family_info: Dict) -> None:
        """가족 관계 정보 업데이트"""
        try:
            # 기존 가족 구성원 정보
            current_members = {
                member["relation"]: member 
                for member in self.profile["user_profile"]["family_info"]["family_members"]
            }

            # 새로운 가족 구성원 정보 업데이트
            new_members = []
            for member in family_info.get("구성원", []):
                relation = member.get("relation")
                if relation:
                    if relation in current_members:
                        # 기존 구성원 정보 업데이트
                        current_members[relation].update(member)
                    else:
                        # 새로운 구성원 추가
                        new_members.append(member)

            # 가족 정보 업데이트
            self.profile["user_profile"]["family_info"].update({
                "family_members": list(current_members.values()) + new_members,
                "household_size": family_info.get("가구_크기"),
                "living_arrangement": family_info.get("동거_여부"),
                "dependents": [
                    member for member in (list(current_members.values()) + new_members)
                    if member.get("is_dependent", False)
                ]
            })

            logger.info("가족 관계 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"가족 관계 정보 업데이트 중 오류: {str(e)}")

    def _update_professional_info(self, job_info: Dict) -> None:
        """직업 정보 업데이트"""
        try:
            workplace = job_info["직장"]
            job_role = job_info["직무"]

            # 업종 추론
            if not workplace.get("업종"):
                workplace["업종"] = self._infer_industry(workplace.get("회사명"))

            # 직업 정보 업데이트
            self.profile["user_profile"]["professional_info"].update({
                "company_name": workplace.get("회사명"),
                "industry": workplace.get("업종"),
                "work_address": workplace.get("근무지"),
                "position": job_role.get("직위"),
                "occupation": job_role.get("역할"),
                "work_hours": job_info.get("근무형태")
            })

            # 직장 변경 시 이력 추가
            if workplace.get("회사명"):
                self._update_employment_history(workplace["회사명"], job_role.get("직위"))

            logger.info("직업 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"직업 정보 업데이트 중 오류: {str(e)}")

    def _update_residence_info(self, residence_info: Dict) -> None:
        """거주 정보 업데이트"""
        try:
            address = residence_info["주소"]

            # 도시 정보 추론
            if not address.get("도시") and address.get("동네"):
                address["도시"] = self._infer_city(address["동네"])

            current_address = " ".join(filter(None, [
                address.get("도시"),
                address.get("동네"),
                address.get("상세주소")
            ]))

            if current_address:
                # 기존 주소가 있으면 이력에 추가
                old_address = self.profile["user_profile"]["residence_info"]["current_address"]
                if old_address and old_address != current_address:
                    self.profile["user_profile"]["residence_info"]["previous_addresses"].append({
                        "address": old_address,
                        "end_date": datetime.now().strftime("%Y-%m-%d")
                    })

                # 새로운 주소 정보 업데이트
                self.profile["user_profile"]["residence_info"].update({
                    "current_address": current_address,
                    "housing_type": residence_info.get("주거형태"),
                    "ownership_status": residence_info.get("점유형태"),
                    "residence_period": residence_info.get("거주기간")
                })

            logger.info("거주 정보 업데이트 완료")
        except Exception as e:
            logger.error(f"거주 정보 업데이트 중 오류: {str(e)}")

    def _update_employment_history(self, company: str, position: Optional[str]) -> None:
        """직장 이력 업데이트"""
        try:
            employment_history = self.profile["user_profile"]["professional_info"]["employment_history"]
            if employment_history:
                last_job = employment_history[-1]
                if last_job["company"] != company:
                    employment_history.append({
                        "company": company,
                        "position": position,
                        "start_date": datetime.now().strftime("%Y-%m-%d")
                    })
            else:
                employment_history.append({
                    "company": company,
                    "position": position,
                    "start_date": datetime.now().strftime("%Y-%m-%d")
                })

            logger.info("직장 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"직장 이력 업데이트 중 오류: {str(e)}")

    def _infer_industry(self, company_name: str) -> Optional[str]:
        """회사명으로 업종 추론"""
        try:
            # 주요 업종별 키워드 매핑
            industry_keywords = {
                "IT/기술": ["테크", "소프트웨어", "시스템", "솔루션", "IT", "정보통신"],
                "금융": ["은행", "증권", "보험", "카드", "캐피탈", "금융"],
                "제조": ["전자", "자동차", "화학", "제철", "중공업"],
                "유통/서비스": ["마트", "백화점", "쇼핑", "호텔", "리테일"],
                "통신": ["텔레콤", "통신", "모바일"],
                "교육": ["학원", "교육", "스쿨", "러닝"],
                "의료/제약": ["병원", "제약", "바이오", "메디컬", "헬스케어"]
            }

            if not company_name:
                return None

            company_name = company_name.lower()
            for industry, keywords in industry_keywords.items():
                if any(keyword.lower() in company_name for keyword in keywords):
                    logger.info(f"업종 추론 결과: {industry} (회사명: {company_name})")
                    return industry

            logger.info("업종 업데이트 완료")
            return "기타"
        except Exception as e:
            logger.error(f"업종 추론 중 오류: {str(e)}")
            return None

    def _infer_city(self, district: str) -> Optional[str]:
        """동네명으로 도시 추론"""
        try:
            # 주요 도시별 행정구역 매핑
            city_districts = {
                "서울": ["강남구", "서초구", "송파구", "강동구", "마포구", "용산구", 
                        "성동구", "광진구", "중구", "종로구", "동대문구", "성북구",
                        "강북구", "도봉구", "노원구", "중랑구", "은평구", "서대문구",
                        "강서구", "양천구", "구로구", "금천구", "영등포구", "동작구", "관악구"],
                "부산": ["중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구",
                        "북구", "해운대구", "사하구", "금정구", "강서구", "연제구",
                        "수영구", "사상구", "기장군"],
                "인천": ["중구", "동구", "미추홀구", "연수구", "남동구", "부평구",
                        "계양구", "서구", "강화군", "옹진군"]
            }

            if not district:
                return None

            # 구/동 분리
            district_parts = district.split()
            for part in district_parts:
                for city, districts in city_districts.items():
                    if any(dist in part for dist in districts):
                        logger.info(f"도시 추론 결과: {city} (행정구역: {district})")
                        return city

            logger.info("도시 업데이트 완료")
            return None
        except Exception as e:
            logger.error(f"도시 추론 중 오류: {str(e)}")
            return None

    def _merge_with_context(self, current_analysis: Dict, context: Dict) -> Dict:
        """
        현재 분석 결과와 이전 컨텍스트를 병합

        Args:
            current_analysis: 현재 분석 결과
            context: 관련된 이전 컨텍스트

        Returns:
            Dict: 병합된 분석 결과
        """
        try:
            merged = current_analysis.copy()

            # 1. 주제 연속성 확인 및 보완
            if not merged.get("main_topic") and context.get("main_topic"):
                merged["main_topic"] = context["main_topic"]

            # 2. 서브 토픽 병합
            merged_sub_topics = merged.get("sub_topics", {})
            context_sub_topics = context.get("sub_topics", {})

            for category in ["activities", "temporal", "spatial", "companions"]:
                current_items = set(merged_sub_topics.get(category, []))
                context_items = set(context_sub_topics.get(category, []))

                # 현재 항목이 비어있으면 컨텍스트에서 가져옴
                if not current_items and context_items:
                    merged_sub_topics[category] = list(context_items)
                # 현재 항목이 있으면 컨텍스트와 병합
                elif current_items and context_items:
                    merged_sub_topics[category] = list(current_items | context_items)

            merged["sub_topics"] = merged_sub_topics

            # 3. 키워드 보완
            current_keywords = set(merged.get("keywords", []))
            context_keywords = set(context.get("keywords", []))
            if current_keywords or context_keywords:
                merged["keywords"] = list(current_keywords | context_keywords)

            # 4. 감정 상태 연속성 처리
            if not merged.get("sentiment") and context.get("sentiment"):
                merged["sentiment"] = context["sentiment"]
            elif merged.get("sentiment") and context.get("sentiment"):
                # 감정 강도 평균 계산
                current_intensity = merged["sentiment"].get("intensity", 50)
                context_intensity = context["sentiment"].get("intensity", 50)
                merged["sentiment"]["intensity"] = (current_intensity + context_intensity) # 2

            # 5. 신뢰도 점수 조정
            if context.get("reliability_score"):
                context_weight = 0.3  # 컨텍스트 가중치
                current_score = merged.get("reliability_score", 0)
                context_score = context.get("reliability_score", 0)
                merged["reliability_score"] = int(
                    current_score * (1 - context_weight) + 
                    context_score * context_weight
                )

            # 6. 의도 연속성 처리
            if not merged.get("intent") or merged["intent"] == "unknown":
                merged["intent"] = context.get("intent", "unknown")

            logger.debug(f"컨텍스트 병합 완료: {merged}")
            return merged
        except Exception as e:
            logger.error(f"Error merging with context: {str(e)}")
            return current_analysis

    def _map_domain(self, topic: str) -> str:
        """토픽을 도메인으로 매핑"""
        try:
            mapped_domain = DomainMapper.map_topic_to_domain(topic)
            if mapped_domain == Domain.UNKNOWN.value:
                logger.warning(f"Unknown topic: {topic}")
            return mapped_domain
        except Exception as e:
            logger.error(f"Error mapping domain: {str(e)}")
            return Domain.UNKNOWN.value

    def get_profile(self) -> Dict:
        """전체 프로필 정보 반환"""
        try:
            logger.debug("프로필 정보 조회 시작")
            profile_data = {
                "version": self.profile_version,
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "user_profile": self.profile["user_profile"],
                "user_interests": self._get_interests_summary(),
                "behavior_patterns": self._get_behavior_summary(),
                "knowledge_base": self._get_knowledge_summary(),
                "activities": self._get_activities_summary(),
                "context_memory": self._get_memory_summary(),
                "interaction_metrics": self._get_metrics_summary()
            }
            logger.debug(f"프로필 정보 조회 완료: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
            return profile_data
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return {}

    def _get_interests_summary(self) -> Dict:
        """관심사 요약 정보"""
        return {
            "top_topics": self._get_top_items(self.interests.topics),
            "top_keywords": self._get_top_items(self.interests.keywords),
            "preferences": {
                category: self._get_top_items(prefs)
                for category, prefs in self.interests.preferences.items()
            }
        }

    def _get_behavior_summary(self) -> Dict:
        """행동 패턴 요약 정보"""
        return {
            "temporal": {
                period: self._get_top_items(patterns)
                for period, patterns in self.behavior.temporal.items()
            },
            "spatial": {
                category: self._get_top_items(patterns)
                for category, patterns in self.behavior.spatial.items()
            },
            "social": {
                context: self._get_top_items(patterns)
                for context, patterns in self.behavior.social.items()
            }
        }

    def _get_knowledge_summary(self) -> Dict:
        """지식 기반 요약 정보"""
        try:
            return {
                "domains": {
                    domain: {
                        "frequency": info.get("frequency", 0),
                        "top_topics": self._get_top_items(self._flatten_topics(info.get("topics", {}))),
                        "top_preferences": self._get_top_items(info.get("preferences", {}))
                    }
                    for domain, info in self.knowledge.domains.items()
                },
                "cross_domain_patterns": self._get_top_items(
                    self.knowledge.cross_domain_patterns
                )
            }
        except Exception as e:
            logger.error(f"Error getting knowledge summary: {str(e)}")
            return {}

    def _flatten_topics(self, topics: Dict) -> Dict:
        """중첩된 토픽 구조를 평면화"""
        flattened = {}
        try:
            for category, items in topics.items():
                if isinstance(items, dict):
                    for topic, count in items.items():
                        flattened[f"{category}:{topic}"] = count
                else:
                    flattened[category] = items
            return flattened
        except Exception as e:
            logger.error(f"Error flattening topics: {str(e)}")
            return {}

    def _get_activities_summary(self) -> Dict:
        """활동 요약 정보"""
        return {
            "recent_activities": self._get_recent_activities(),
            "recurring_patterns": {
                period: len(activities)
                for period, activities in self.activities.recurring.items()
            },
            "activity_stats": self.activities.get_activity_summary()
        }

    def _get_memory_summary(self) -> Dict:
        """메모리 요약 정보"""
        return {
            "recent_context": self.context.get_recent_context(),
            "long_term_patterns": self._get_top_items(
                self.context.long_term.get("patterns", {})
            )
        }

    def _get_metrics_summary(self) -> Dict:
        """메트릭스 요약 정보"""
        return self.metrics.get_metrics_summary()

    def save_profile(self, filepath: str) -> None:
        """프로필 상태 저장"""
        try:
            profile_data = self.get_profile()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")

    def load_profile(self, filepath: str) -> None:
        """프로필 상태 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)

            # 각 컴포넌트 상태 복원
            self._restore_components(profile_data)

            # 메타데이터 복원
            self.profile_version = profile_data.get("version", "1.0.0")
            last_update = profile_data.get("last_update")
            if last_update:
                self.last_update = datetime.fromisoformat(last_update)

        except Exception as e:
            logger.error(f"Error loading profile: {str(e)}")

    def _restore_components(self, profile_data: Dict) -> None:
        """컴포넌트 상태 복원"""
        try:
            if "user_interests" in profile_data:
                self.interests = UserInterests()
                # 관심사 데이터 복원 로직

            if "behavior_patterns" in profile_data:
                self.behavior = BehaviorPatterns()
                # 행동 패턴 데이터 복원 로직

            if "knowledge_base" in profile_data:
                self.knowledge = KnowledgeBase()
                # 지식 베이스 데이터 복원 로직

            if "activities" in profile_data:
                self.activities = Activities()
                # 활동 데이터 복원 로직

            if "context_memory" in profile_data:
                self.context = ContextMemory()
                # 컨텍스트 메모리 데이터 복원 로직

            if "interaction_metrics" in profile_data:
                self.metrics = InteractionMetrics()
                # 상호작용 메트릭스 데이터 복원 로직

        except Exception as e:
            logger.error(f"Error restoring components: {str(e)}")

    def _get_top_items(self, data: Dict, limit: int = 5) -> List[tuple]:
        """상위 항목 반환"""
        try:
            # 데이터가 중첩 딕셔너리인 경우 처리
            if any(isinstance(v, dict) for v in data.values()):
                # 중첩된 딕셔너리의 경우 각 하위 딕셔너리의 값들의 합계를 사용
                flattened_data = {
                    k: sum(v.values()) if isinstance(v, dict) else v 
                    for k, v in data.items()
                }
            else:
                flattened_data = data

            # 숫자가 아닌 값은 0으로 처리
            sorted_items = sorted(
                flattened_data.items(),
                key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0,
                reverse=True
            )
            return sorted_items[:limit]
        except Exception as e:
            logger.error(f"Error in _get_top_items: {str(e)}")
            return []

    def _get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """최근 활동 목록 반환"""
        all_activities = (
            self.activities.completed +
            self.activities.planned
        )
        sorted_activities = sorted(
            all_activities,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        return sorted_activities[:limit]

    def get_suggested_actions(self, domain: str) -> List[str]:
        """도메인별 추천 활동"""
        try:
            suggestions = []

            # 1. 관심사 기반 추천
            interest_based = self.interests.get_top_interests("activities")
            if interest_based:
                suggestions.extend([f"Try {activity}" for activity, _ in interest_based])

            # 2. 행동 패턴 기반 추천
            pattern_based = self.behavior.temporal.get("periodic", {})
            if pattern_based:
                suggestions.extend([f"Continue {activity}" for activity in pattern_based])

            # 3. 도메인 지식 기반 추천
            domain_knowledge = self.knowledge.get_domain_knowledge(domain)
            if domain_knowledge and "preferences" in domain_knowledge:
                preferences = domain_knowledge["preferences"]
                for pref_type, prefs in preferences.items():
                    if prefs:
                        top_pref = max(prefs.items(), key=lambda x: x[1])[0]
                        suggestions.append(f"Consider {top_pref} for {pref_type}")

            return suggestions[:5]  # 최대 5개 추천
        except Exception as e:
            logger.error(f"Error getting suggested actions: {str(e)}")
            return []

    def get_related_topics(self, domain: str) -> List[str]:
        """연관 주제 추천"""
        try:
            related_topics = []

            # 1. 도메인 지식에서 연관 주제 추출
            domain_info = self.knowledge.get_domain_knowledge(domain)
            if domain_info and "topics" in domain_info:
                related_topics.extend(
                    [topic for topic, _ in self._get_top_items(domain_info["topics"])]
                )

            # 2. 컨텍스트 메모리에서 연관 주제 추출
            recent_context = self.context.get_recent_context(3)
            for context in recent_context:
                if context.get("topic") != domain:
                    related_topics.append(context.get("topic"))

            return list(set(related_topics))  # 중복 제거
        except Exception as e:
            logger.error(f"Error getting related topics: {str(e)}")
            return []

    def get_personalized_suggestions(self, domain: str) -> List[str]:
        """개인화된 추천 생성"""
        try:
            logger.info(f"개인화된 추천 생성 시작 - 도메인: {domain}")
            suggestions = []

            # 1. 최근 활동 기반 추천
            recent_activities = self.activities.get_activity_summary()
            if recent_activities and "completed_activities" in recent_activities:
                completed = recent_activities["completed_activities"]
                if completed > 0:
                    activity_patterns = recent_activities.get("activity_patterns", {})
                    frequency = activity_patterns.get("frequency", {})
                    if frequency:
                        try:
                            top_activity = max(
                                frequency.items(), 
                                key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0
                            )[0]
                            suggestions.append(f"Based on your recent {top_activity}")
                            logger.debug(f"활동 기반 추천 생성: {top_activity}")
                        except ValueError as e:
                            logger.warning(f"활동 빈도 처리 중 오류: {str(e)}")

            # 2. 선호도 기반 추천
            if domain in self.interests.preferences:
                prefs = self.interests.preferences[domain]
                if isinstance(prefs, dict) and prefs:
                    try:
                        top_prefs = sorted(
                            prefs.items(),
                            key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0,
                            reverse=True
                        )[:2]
                        suggestions.extend([f"You might enjoy {pref}" for pref, _ in top_prefs])
                        logger.debug(f"선호도 기반 추천 생성: {len(top_prefs)}개")
                    except ValueError as e:
                        logger.warning(f"선호도 정렬 중 오류: {str(e)}")

            # 3. 행동 패턴 기반 추천
            temporal_patterns = self.behavior.temporal.get("periodic", {})
            if temporal_patterns:
                try:
                    top_patterns = sorted(
                        temporal_patterns.items(),
                        key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0,
                        reverse=True
                    )[:1]
                    suggestions.extend([f"Consider scheduling {pattern}" for pattern, _ in top_patterns])
                    logger.debug(f"패턴 기반 추천 생성: {len(top_patterns)}개")
                except ValueError as e:
                    logger.warning(f"패턴 정렬 중 오류: {str(e)}")

            return list(set(suggestions))[:5]  # 중복 제거 및 최대 5개로 제한
        except Exception as e:
            logger.error(f"Error getting personalized suggestions: {str(e)}")
            return ["Try something new"]  # 기본 추천 제공

    def analyze_patterns(self) -> Dict:
        """행동 패턴 분석"""
        try:
            return {
                "temporal": self.behavior.temporal,
                "spatial": self.behavior.spatial,
                "social": self.behavior.social,
                "spending": self.behavior.spending,
                "interaction": self.behavior.interaction_style
            }
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            return {}

    def analyze_trends(self) -> Dict:
        """트렌드 분석"""
        try:
            return {
                "interests": self._analyze_interest_trends(),
                "behavior": self._analyze_behavior_trends(),
                "engagement": self._analyze_engagement_trends()
            }
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _analyze_interest_trends(self) -> Dict:
        """관심사 트렌드 분석"""
        return {
            "rising_topics": self._get_top_items(self.interests.topics),
            "consistent_interests": self._get_top_items(
                self.interests.preferences.get("topics", {})
            )
        }

    def _analyze_behavior_trends(self) -> Dict:
        """행동 패턴 트렌드 분석"""
        return {
            "temporal": self._get_top_items(self.behavior.temporal["periodic"]),
            "spatial": self._get_top_items(self.behavior.spatial["locations"])
        }

    def _analyze_engagement_trends(self) -> Dict:
        """참여도 트렌드 분석"""
        return {
            "recent_engagement": self.metrics.engagement["trends"][-5:],
            "peak_engagement": self.metrics.engagement["peaks"]
        }

    def detect_changes(self) -> Dict:
        """주요 변화 감지"""
        try:
            return {
                "interest_changes": self._detect_interest_changes(),
                "behavior_changes": self._detect_behavior_changes(),
                "engagement_changes": self._detect_engagement_changes()
            }
        except Exception as e:
            logger.error(f"Error detecting changes: {str(e)}")
            return {}

    def _detect_interest_changes(self) -> Dict:
        """관심사 변화 감지"""
        return {
            "new_topics": self._get_recent_items(self.interests.topics),
            "declining_interests": self._get_declining_items(
                self.interests.preferences.get("topics", {})
            )
        }

    def _detect_behavior_changes(self) -> Dict:
        """행동 패턴 변화 감지"""
        return {
            "new_patterns": self._get_recent_items(
                self.behavior.temporal["periodic"]
            ),
            "changing_preferences": self._get_changing_items(
                self.behavior.spatial["locations"]
            )
        }

    def _detect_engagement_changes(self) -> Dict:
        """참여도 변화 감지"""
        trends = self.metrics.engagement["trends"]
        if len(trends) >= 2:
            recent = trends[-1]["score"]
            previous = trends[-2]["score"]
            change = recent - previous
            return {
                "trend": "increasing" if change > 0 else "decreasing",
                "change_amount": abs(change)
            }
        return {"trend": "stable", "change_amount": 0}

    def _get_recent_items(self, data: Dict, days: int = 7) -> List[str]:
        """
        최근 항목 추출

        Args:
            data: 분석할 데이터 딕셔너리
            days: 최근 일수 (기본값: 7일)

        Returns:
            최근 days일 동안의 항목 리스트
        """
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=days)

            recent_items = []
            for item, details in data.items():
                if isinstance(details, dict) and "timestamp" in details:
                    item_time = datetime.fromisoformat(details["timestamp"])
                    if item_time >= cutoff_time:
                        recent_items.append(item)
                elif isinstance(details, (int, float)):
                    # 타임스탬프가 없는 경우 빈도수 기반으로 판단
                    if details > 0:  # 최근에 사용된 것으로 간주
                        recent_items.append(item)

            return sorted(recent_items, 
                        key=lambda x: data[x].get("timestamp", "") if isinstance(data[x], dict) else data[x],
                        reverse=True)
        except Exception as e:
            logger.error(f"Error getting recent items: {str(e)}")
            return []

    def _get_declining_items(self, data: Dict) -> List[str]:
        """
        감소 추세 항목 추출

        Args:
            data: 분석할 데이터 딕셔너리

        Returns:
            감소 추세를 보이는 항목 리스트
        """
        try:
            declining_items = []

            for item, details in data.items():
                if isinstance(details, dict) and "history" in details:
                    # 시계열 데이터가 있는 경우
                    history = details["history"]
                    if len(history) >= 2:
                        recent_avg = sum(history[-3:]) / len(history[-3:])  # 최근 3개 평균
                        past_avg = sum(history[:-3]) / len(history[:-3])    # 이전 데이터 평균

                        if recent_avg < past_avg * 0.8:  # 20% 이상 감소
                            declining_items.append(item)
                elif isinstance(details, (int, float)):
                    # 단순 빈도수의 경우, 임계값 이하인 경우 감소로 간주
                    if details < 3:  # 임계값 설정
                        declining_items.append(item)

            return declining_items
        except Exception as e:
            logger.error(f"Error getting declining items: {str(e)}")
            return []

    def _get_changing_items(self, data: Dict) -> List[str]:
        """
        변화가 있는 항목 추출

        Args:
            data: 분석할 데이터 딕셔너리

        Returns:
            유의미한 변화를 보이는 항목 리스트
        """
        try:
            changing_items = []
            change_threshold = 0.3  # 30% 변화율을 기준으로 설정

            for item, details in data.items():
                if isinstance(details, dict) and "history" in details:
                    # 시계열 데이터가 있는 경우
                    history = details["history"]
                    if len(history) >= 2:
                        recent_value = history[-1]
                        previous_value = history[-2]

                        if previous_value > 0:
                            change_rate = abs(recent_value - previous_value) / previous_value
                            if change_rate >= change_threshold:
                                changing_items.append(item)
                elif isinstance(details, (int, float)):
                    # 단순 빈도수의 경우, 기준값과의 차이로 판단
                    baseline = sum(v for v in data.values() if isinstance(v, (int, float))) / len(data)
                    if abs(details - baseline) / baseline >= change_threshold:
                        changing_items.append(item)

            return changing_items
        except Exception as e:
            logger.error(f"Error getting changing items: {str(e)}")
            return []
