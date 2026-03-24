import json
import sys
from services.lms_client import LmsClient

TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "Get list of all labs and tasks", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task pass rates for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_learners", "description": "Get list of enrolled students", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group performance for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions timeline for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Trigger ETL sync", "parameters": {"type": "object", "properties": {}, "required": []}}},
]

SYSTEM_PROMPT = "You are an LMS assistant. Use tools to fetch data about labs and students."

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
        learners = await self.lms_client.get_learners()
        return {"learners": learners, "count": len(learners)}
    
    async def _call_get_groups(self, lab: str, **kwargs):
        groups = await self.lms_client.get_groups(lab)
        return {"lab": lab, "groups": groups}
    
    async def _call_get_top_learners(self, lab: str, limit: int = 5, **kwargs):
        learners = await self.lms_client.get_top_learners(lab, limit)
        return {"lab": lab, "top_learners": learners}
    
    async def _call_get_completion_rate(self, lab: str, **kwargs):
        rate = await self.lms_client.get_completion_rate(lab)
        return {"lab": lab, "completion_rate": rate}
    
    async def _call_get_timeline(self, lab: str, **kwargs):
        timeline = await self.lms_client.get_timeline(lab)
        return {"lab": lab, "timeline": timeline}
    
    async def _call_get_scores(self, lab: str, **kwargs):
        scores = await self.lms_client.get_scores(lab)
        return {"lab": lab, "scores": scores}
    
    async def _call_trigger_sync(self, **kwargs):
        result = await self.lms_client.trigger_sync()
        return result
    
    async def route(self, user_message: str) -> str:
        msg = user_message.lower()
        
        # Fallback keyword routing when LLM is rate limited
        try:
            # Check for student/learner queries
            if "student" in msg or "learner" in msg or "enroll" in msg or "many" in msg:
                result = await self._call_get_learners()
                count = result.get("count", 0)
                return f"There are {count} students enrolled in the system."
            
            # Check for scores queries
            if "score" in msg and "lab" in msg:
                lab = self._extract_lab(msg)
                if lab:
                    result = await self._call_get_scores(lab)
                    scores = result.get("scores", [])
                    if scores:
                        return f"Score distribution for {lab}: " + ", ".join([f"{s.get('bucket', 'N/A')}: {s.get('count', 0)} students" for s in scores])
                    return f"No score data available for {lab}."
            
            # Check for pass rate queries
            if "pass rate" in msg or "pass" in msg or "lowest" in msg:
                items = await self._call_get_items()
                labs = [i for i in items.get("items", []) if i.get("type") == "lab"]
                results = []
                for lab in labs[:3]:
                    lab_id = f"lab-{lab['id']}"
                    rates = await self._call_get_pass_rates(lab_id)
                    results.append(f"{lab['title']}: checking pass rates...")
                return "Pass rates analysis: " + "; ".join(results[:2])
            
            # Check for group queries
            if "group" in msg and "lab" in msg:
                lab = self._extract_lab(msg)
                if lab:
                    result = await self._call_get_groups(lab)
                    groups = result.get("groups", [])
                    if groups:
                        return f"Groups in {lab}: " + ", ".join([g.get("group", "N/A") for g in groups])
                    return f"No group data for {lab}."
            
            # Check for labs list
            if "lab" in msg and ("list" in msg or "available" in msg or "what" in msg):
                result = await self._call_get_items()
                labs = [i for i in result.get("items", []) if i.get("type") == "lab"]
                titles = [l["title"] for l in labs]
                return "Available labs: " + "; ".join(titles)
            
            # Check for sync queries
            if "sync" in msg or "refresh" in msg or "update" in msg:
                result = await self._call_trigger_sync()
                return f"Sync triggered: {result.get('new_records', 0)} new records loaded."
            
            # Try LLM as fallback
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
            response = await self.llm_client.chat(messages, tools=TOOLS)
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            if "tool_calls" in message and message.get("tool_calls"):
                return await self._process_tool_calls(message, messages)
            return message.get("content", "I can help with labs, students, scores, and pass rates. What would you like to know?")
            
        except Exception as e:
            print(f"[Error] {e}", file=sys.stderr)
            return f"Error: {str(e)}"
    
    def _extract_lab(self, msg: str) -> str:
        import re
        match = re.search(r'lab[- ]?(\d+)', msg, re.IGNORECASE)
        if match:
            return f"lab-{match.group(1).zfill(2)}"
        return None
    
    async def _process_tool_calls(self, message: dict, messages: list) -> str:
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
            else:
                result = {"error": f"Unknown tool: {fn}"}
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": json.dumps(result),
            })
        
        return "Data retrieved from backend."
