import json
from langgraph.graph import StateGraph, START, END
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate
from app.schemas import AgentState

# 🧠 Upstage LLM 초기화
llm = ChatUpstage(model="solar-pro")

def route_by_turn(state: AgentState) -> str:
    """유저의 채팅 횟수를 정확히 카운트하여 6번의 턴을 칼같이 분배한다."""
    history = state.get("history", [])
    user_answers = [msg for msg in history if msg.get("role") == "user"]
    turn_count = len(user_answers)

    if turn_count == 0:
        return "investor"           # [Q1] 투자자 기본 질문
    elif turn_count == 1:
        return "investor_followup"  # [Q2] 투자자 꼬리질문
    elif turn_count == 2:
        return "cto"                # [Q3] CTO 기본 질문
    elif turn_count == 3:
        return "cto_followup"       # [Q4] CTO 꼬리질문
    elif turn_count == 4:
        return "mentor"             # [Q5] 멘토 기본 질문
    elif turn_count == 5:
        return "mentor_followup"    # [Q6] 멘토 꼬리질문
    else:
        return "compile_report"     # [최종] 6번 방어 후 종합 리포트 출력

# ----------------- [1. 💼 투자자 노드] -----------------
async def investor_agent_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    prompt = PromptTemplate.from_template(
        "너는 깐깐한 벤처캐피탈 투자자다. 기획서를 읽고 시장성과 수익성 관점에서 뼈아픈 압박 질문을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. 실제 심사위원이 육성으로 묻는 것처럼 '대화체'로만 작성해라.\n"
        "2. 부연 설명, 배경 설명, 조언은 절대 적지 마라.\n"
        "3. 오직 하나의 질문 문단만 군더더기 없이 출력해라.\n\n"
        "[기획서]\n{text}"
    )
    res = await (prompt | llm).ainvoke({"text": text})
    return {"final_answer": res.content, "domain": "investor"}

async def investor_followup_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    user_defense = state.get("query", "")
    prompt = PromptTemplate.from_template(
        "너는 깐깐한 투자자다. 네가 방금 던진 질문에 대해 유저가 아래와 같이 방어 논리를 펼쳤다. 이 방어 논리의 현실적인 약점이나 비즈니스 모델의 맹점을 파고드는 '꼬리질문'을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. '대화체'로 짧고 날카롭게 찔러라.\n"
        "2. 부연 설명 절대 금지.\n\n"
        "[기획서]\n{text}\n\n[유저의 첫 방어]\n{defense}"
    )
    res = await (prompt | llm).ainvoke({"text": text, "defense": user_defense})
    return {"final_answer": res.content, "domain": "investor"}

# ----------------- [2. 💻 CTO 노드] -----------------
async def cto_agent_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    prompt = PromptTemplate.from_template(
        "너는 냉철한 CTO다. 앞선 투자자의 질의응답은 끝났다. 이제 기획서를 보고, 기술 구현 가능성, 시스템 아키텍처 관점에서 완전히 새로운 기술 압박 질문을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. '대화체'로만 작성.\n"
        "2. 부연 설명 절대 금지.\n\n"
        "[기획서]\n{text}"
    )
    res = await (prompt | llm).ainvoke({"text": text})
    return {"final_answer": res.content, "domain": "cto"}

async def cto_followup_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    user_defense = state.get("query", "")
    prompt = PromptTemplate.from_template(
        "너는 냉철한 CTO다. 유저가 기술 방어 논리를 펼쳤다. 이 논리에서 발생할 수 있는 시스템 병목, 예외 처리 누락 등 기술적 부작용을 파고드는 '기술 꼬리질문'을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. '대화체'로 짧고 날카롭게 작성.\n"
        "2. 부연 설명 금지.\n\n"
        "[기획서]\n{text}\n\n[유저의 기술 방어]\n{defense}"
    )
    res = await (prompt | llm).ainvoke({"text": text, "defense": user_defense})
    return {"final_answer": res.content, "domain": "cto"}

# ----------------- [3. 🦉 멘토 노드] -----------------
async def mentor_agent_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    prompt = PromptTemplate.from_template(
        "너는 예리한 프로젝트 멘토다. 앞선 심사위원들의 검증은 끝났다. 기획서의 논리적 일관성과 프로젝트 핵심 타깃(MVP) 관점에서 근본적인 일침을 가하는 질문을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. '대화체'로만 작성.\n"
        "2. 부연 설명 금지.\n\n"
        "[기획서]\n{text}"
    )
    res = await (prompt | llm).ainvoke({"text": text})
    return {"final_answer": res.content, "domain": "mentor"}

async def mentor_followup_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    user_defense = state.get("query", "")
    prompt = PromptTemplate.from_template(
        "너는 예리한 멘토다. 유저가 방금 너의 일침에 대해 방어 논리를 펼쳤다. 이 답변에서 보이는 타깃 사용자 니즈 파악의 오류나 기획의 허점을 마지막으로 한 번 더 파고드는 '최종 꼬리질문'을 딱 1개만 던져라.\n\n"
        "🚨 [절대 규칙]\n"
        "1. '대화체'로 짧고 날카롭게 찔러라.\n"
        "2. 부연 설명 금지.\n\n"
        "[기획서]\n{text}\n\n[유저의 방어 논리]\n{defense}"
    )
    res = await (prompt | llm).ainvoke({"text": text, "defense": user_defense})
    return {"final_answer": res.content, "domain": "mentor"}

# ----------------- [4. 📊 종합 리포트 노드] -----------------
async def final_report_node(state: AgentState) -> dict:
    text = state.get("proposal_text", "")
    history = state.get("history", [])
    history_text = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in history])
    
    # 🎯 기획서 요구사항 ④번 스펙을 프롬프트 포맷으로 강제 바인딩
    prompt = PromptTemplate.from_template(
        "너는 다중 페르소나 심사위원단을 이끄는 오케스트레이터이자 심사위원장이다.\n"
        "제공된 기획서 원문과 그동안 진행된 6번의 압박 면접 대화 기록(history)을 기반으로, "
        "반드시 다음 3가지 섹션 양식에 맞춰 최종 피드백 리포트를 작성해라. 마크다운 문법을 적극 활용해라.\n\n"
        "1. 🎤 진행된 질문 목록\n"
        "- 대화 기록에서 투자자, CTO, 멘토가 던진 핵심 질문들을 요약하여 리스트로 정리해라.\n\n"
        "2. ⚠️ 핵심 허점 및 위험도 진단\n"
        "반드시 아래 포맷의 마크다운 표(Table) 형태로 출력해라. 위험도는 반드시 '상', '중', '하' 중 하나로 산정해라.\n"
        "| 진단 항목 | 위험도 | 발견된 논리적/기술적 허점 내용 |\n"
        "| --- | --- | --- |\n"
        "| 시장성 및 차별성 | [위험도] | 내용 |\n"
        "| 기술 실현 가능성 | [위험도] | 내용 |\n"
        "| 논리 일관성 및 범위 | [위험도] | 내용 |\n\n"
        "3. 💡 향후 기획서 보완 제안\n"
        "- 본발표 및 평가 통과를 위해 기획서에서 당장 고쳐야 할 구체적인 행동 가이드(Action Item)를 제안해라.\n\n"
        "[기획서 원문]\n{text}\n\n"
        "[전체 대화 기록]\n{history}"
    )
    res = await (prompt | llm).ainvoke({"text": text, "history": history_text})
    return {"final_answer": f"📋 **[AI 모의 심사 최종 검증 성적표]**\n\n{res.content}", "domain": "report"}

# ========================================================
# 🕸️ LangGraph 컴파일 (경로 연결)
# ========================================================
def create_graph():
    builder = StateGraph(AgentState)

    builder.add_node("investor", investor_agent_node)
    builder.add_node("investor_followup", investor_followup_node)
    builder.add_node("cto", cto_agent_node)
    builder.add_node("cto_followup", cto_followup_node)
    builder.add_node("mentor", mentor_agent_node)
    builder.add_node("mentor_followup", mentor_followup_node)
    builder.add_node("compile_report", final_report_node)

    builder.add_conditional_edges(
        START,
        route_by_turn,
        {
            "investor": "investor",
            "investor_followup": "investor_followup",
            "cto": "cto",
            "cto_followup": "cto_followup",
            "mentor": "mentor",
            "mentor_followup": "mentor_followup",
            "compile_report": "compile_report"
        }
    )
    
    builder.add_edge("investor", END)
    builder.add_edge("investor_followup", END)
    builder.add_edge("cto", END)
    builder.add_edge("cto_followup", END)
    builder.add_edge("mentor", END)
    builder.add_edge("mentor_followup", END)
    builder.add_edge("compile_report", END)

    return builder.compile()