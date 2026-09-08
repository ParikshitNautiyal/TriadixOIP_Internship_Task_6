"""test.py -- batch-run the RAG pipeline against a set of questions."""
from fastapi import APIRouter, HTTPException, Request

from app.config import RATE_LIMIT_TEST
from app.ratelimit import limiter
from app.schemas import DefaultQuestionsResponse, SourceOut, TestCaseOut, TestRequest, TestResponse
from app.testing import DEFAULT_TEST_QUESTIONS, run_test_suite
from app.vector_store import get_store

router = APIRouter(prefix="/api/test", tags=["Testing"])


@router.get("/default-questions", response_model=DefaultQuestionsResponse)
def default_questions():
    return DefaultQuestionsResponse(questions=DEFAULT_TEST_QUESTIONS)


@router.post("", response_model=TestResponse)
@limiter.limit(RATE_LIMIT_TEST)
def run_tests(request: Request, payload: TestRequest):
    store = get_store()
    if store.count() == 0:
        raise HTTPException(400, "Process at least one document before running tests.")

    questions = payload.questions or DEFAULT_TEST_QUESTIONS
    questions = [q for q in questions if q and q.strip()]
    if not questions:
        raise HTTPException(400, "No non-empty questions provided.")

    raw_results = run_test_suite(questions, store)
    return TestResponse(results=[
        TestCaseOut(
            question=r.question,
            num_chunks_retrieved=r.num_chunks_retrieved,
            top_distance=r.top_distance,
            answer=r.answer,
            sources=[SourceOut(**s) for s in r.sources],
            grounded=r.grounded,
        )
        for r in raw_results
    ])
