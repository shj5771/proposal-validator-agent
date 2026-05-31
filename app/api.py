import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest, ChatResponse, StreamEvent
from app.graph import create_graph

router = APIRouter()
graph = create_graph()

def build_initial_state(request: ChatRequest) -> dict:
    """프론트엔드에서 받은 기획서와 대화 기록을 Graph State로 묶는다."""
    return {
        "query": request.message,
        "proposal_text": request.proposal_text,
        "history": request.history,
        "final_answer": "",
        "domain": "architecture"
    }

@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest):
    """동기 방식으로 현재 턴의 심사위원 피드백을 반환한다."""
    result = await graph.ainvoke(build_initial_state(request))
    return ChatResponse(
        answer=result.get("final_answer", ""), 
        domain=result.get("domain", "")
    )

@router.post("/chat")
async def chat_stream(request: ChatRequest):
    """(호환성 유지용) 최초 업로드 시 첫 심사위원의 응답을 반환한다."""
    async def gen():
        result = await graph.ainvoke(build_initial_state(request))
        done = StreamEvent(
            event="done",
            data=json.dumps({"answer": result.get("final_answer", ""), "domain": result.get("domain", "")}, ensure_ascii=False)
        )
        yield f"data: {done.model_dump_json()}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")