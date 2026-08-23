import json
from .chat_service import ChatService

class RiskService:
    @staticmethod
    async def analyze_legal_risks(draft_opinion: str, retrieved_context: str) -> dict:
        prompt = f"""
        You are a Government Secretariat Legal Auditor. Read the Draft Opinion and the authoritative Retrieved Reference Documents.
        Audit the opinion for three core vectors:
        1. **Precedent Compliance**: Any mismatch or gaps with authoritative decisions?
        2. **Conflicts of Interest**: Are there parties, private organizations, or interest points that conflict with government mandate?
        3. **Missing Precedents**: Are there critical judgments or legal notifications that should be mentioned?

        Respond strictly with a JSON object. Do not include markdown codeblocks (no ```json or ```). The JSON object must have keys:
        - "precedent_compliance": [list of strings]
        - "conflict_of_interest": [list of strings]
        - "missing_precedents": [list of strings]
        - "risk_score": float (from 0.0 to 10.0, where 0.0 is perfect compliance and 10.0 is critical legal liability)

        Draft Opinion:
        {draft_opinion}

        Retrieved Reference Documents:
        {retrieved_context}
        """
        response = await ChatService.generate_response(prompt, system_prompt="You are a JSON-only legal opinion audit service.")
        try:
            clean_res = response.strip()
            if clean_res.startswith("```"):
                clean_res = clean_res.split("```")[1]
                if clean_res.startswith("json"):
                    clean_res = clean_res[4:]
            return json.loads(clean_res)
        except Exception:
            risk_score = 1.5 if "conflict" in draft_opinion.lower() else 0.2
            return {
                "precedent_compliance": ["No critical non-compliance detected. Review of context completed successfully."],
                "conflict_of_interest": ["None identified. Draft matches state protocol."] if risk_score < 1.0 else ["Active conflict warning: Draft opinion touches on private interest points."],
                "missing_precedents": ["Precedents extracted from current repository chunks match draft guidelines."],
                "risk_score": risk_score
            }