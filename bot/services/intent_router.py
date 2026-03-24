import json
import sys
from services.lms_client import LmsClient

TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "Get list of all labs and tasks. Use this to discover available labs.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task pass rates and attempt counts for a specific lab. Use when user asks about scores, pass rates, or how students are doing in a lab.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier like 'lab-01', 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_learners", "description": "Get list of enrolled students and their groups. Use when user asks about students, enrollment, or how many learners.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group performance and student counts for a lab. Use when comparing groups or asking which group is best.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab. Use when user asks about best students, top performers, or leaderboard.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier"}, "limit": {"type": "integer", "description": "Number of top learners (default 5)"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab. Use when user asks about completion or how many finished.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions timeline (per day) for a lab. Use when user asks about activity over time or submission patterns.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution (4 buckets) for a lab. Use when user asks about score distribution or grade breakdown.", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to sync, refresh, or update data.", "parameters": {"type": "object", "properties": {}, "required": []}}},
]

SYSTEM_PROMPT = """You are an LMS assistant. You have access to tools that fetch data about labs, tasks, students, and analytics.
When a user asks a question, use the available tools to get the data needed to answer.
Always call tools when you need data - don't make up information.
After getting tool results, analyze the data and provide a helpful answer with specific numbers and names from the data.
If the user's message is a greeting, respond naturally without using tools.
If you don't understand the query, ask for clarification or suggest what you can help with."""

class IntentRouter:
    def __init__(self, llm_client, lms_client):
        self.llm_client = llm_client
        self.lms_client = lms_client
        self.tool_functions = {
            "get_items": self._call_get_items,
            "get_pass_rates": self._call_get_pass_rates,
            "get_learners": self._call_get_learners,
            "get_groups": self._call_get_groups,
            "get_top_learners": self._call_get_top_learners,
            "get_completion_rate": self._call_get_completion_rate,
            "get_timeline": self._call_get_timeline,
            "get_scores": self._call_get_scores,
            "trigger_sync": self._call_trigger_sync,
        }
    
    async def _call_get_items(self, **kwargs):
        items = await self.lms_client.get_items()
        return {"items": items, "count": len(items)}
    
    async def _call_get_pass_rates(self, lab: str):
        rates = await self.lms_client.get_pass_rates(lab)
        return {"lab": lab, "pass_rates": rates}
    
    async def _call_get_learners(self, **kwargs):
        return {"learners": [], "count": 0}
    
    async def _call_get_groups(self, lab: str, **kwargs):
        return {"lab": lab, "groups": []}
    
    async def _call_get_top_learners(self, lab: str, limit: int = 5, **kwargs):
        return {"lab": lab, "top_learners": [], "limit": limit}
    
    async def _call_get_completion_rate(self, lab: str, **kwargs):
        return {"lab": lab, "completion_rate": 0}
    
    async def _call_get_timeline(self, lab: str, **kwargs):
        return {"lab": lab, "timeline": []}
    
    async def _call_get_scores(self, lab: str, **kwargs):
        return {"lab": lab, "scores": []}
    
    async def _call_trigger_sync(self, **kwargs):
        return {"status": "sync triggered", "new_records": 0, "total_records": 0}
    
    async def route(self, user_message: str) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
        max_iterations = 5
        
        for iteration in range(max_iterations):
            try:
                response = await self.llm_client.chat(messages, tools=TOOLS)
            except Exception as e:
                print(f"[LLM error] {e}", file=sys.stderr)
                return f"LLM error: {str(e)}"
            
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            if "tool_calls" not in message or not message.get("tool_calls"):
                content = message.get("content", "I didn't understand. Try asking about labs, scores, or students.")
                return content
            
            tool_calls = message.get("tool_calls", [])
            messages.append(message)
            
            for tc in tool_calls:
                fn = tc.get("function", {}).get("name", "")
                args_str = tc.get("function", {}).get("arguments", "{}")
                try:
                    args = json.loads(args_str) if args_str else {}
                except:
                    args = {}
                
                print(f"[tool] LLM called: {fn}({args})", file=sys.stderr)
                
                tool_func = self.tool_functions.get(fn)
                if tool_func:
                    try:
                        result = await tool_func(**args)
                        print(f"[tool] Result: {json.dumps(result)[:200]}", file=sys.stderr)
                    except Exception as e:
                        result = {"error": str(e)}
                        print(f"[tool] Error: {e}", file=sys.stderr)
                else:
                    result = {"error": f"Unknown tool: {fn}"}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": json.dumps(result),
                })
            
            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
        
        return "I need more information to answer that question."
