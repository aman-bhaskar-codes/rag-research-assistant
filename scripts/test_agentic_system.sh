#!/bin/bash
set -e
BASE="http://localhost:8000"
echo "=== AGENTIC SYSTEM TEST SUITE ==="

echo ""
echo "1. Health check..."
curl -sf $BASE/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok', f'Health failed: {d}'
print(f'   ✓ DB: {d[\"db\"]}, Redis: {d[\"redis\"]}, Ollama: {d[\"ollama\"]}')
"

echo ""
echo "2. Capability map..."
curl -sf $BASE/agent/capability-map | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   ✓ {len(d[\"capability_map\"])} categories tracked')
"

echo ""
echo "3. Agent run test (simple task, 30s timeout)..."
TASK='What is retrieval-augmented generation and what are its main components?'
python3 << 'PYEOF'
import asyncio, json, httpx

async def test_agent():
    events = {'sources': 0, 'thinking': 0, 'steps': 0, 'done': False}
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", "http://localhost:8000/agent/run",
            json={"task": "What is RAG?", "session_id": "test-123", "max_steps": 5}
        ) as resp:
            event_type = ""
            async for line in resp.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                elif line.startswith("data: "):
                    if event_type == "agent_step": events['steps'] += 1
                    if event_type == "final_answer": events['done'] = True; break

    print(f"   ✓ Steps: {events['steps']}, Done: {events['done']}")
    assert events['steps'] > 0, "No steps executed"
    assert events['done'], "No final answer"

asyncio.run(test_agent())
PYEOF

echo ""
echo "4. Pending strategy approvals..."
curl -sf $BASE/agent/strategies/pending | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   ✓ {d[\"count\"]} strategies pending approval')
"

echo ""
echo "=== ALL TESTS PASSED ==="
echo ""
echo "System URLs:"
echo "  API:         http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Frontend:    http://localhost:3000"
echo "  Agent Page:  http://localhost:3000/agent"
