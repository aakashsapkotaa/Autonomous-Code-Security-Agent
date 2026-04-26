"""
OpenRouter AI Client — generates security fix suggestions.
"""
import httpx
import json
import re
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model   = model   or os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout  = 60.0

    # ── Low-level call ────────────────────────────────────────────────────────

    async def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 800) -> Dict:
        if not self.api_key or self.api_key in ("", "your-openrouter-key", "your_private_key"):
            raise ValueError("OPENROUTER_API_KEY is not set in backend/.env")

        logger.info(f"[openrouter] calling model={self.model} tokens={max_tokens}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model":      self.model,
                    "messages":   [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens":  max_tokens,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                    "HTTP-Referer":  "https://secureshift.io",
                    "X-Title":       "SecureShift",
                },
            )
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            logger.debug(f"[openrouter] raw response: {content[:300]}")
            return {"response": content, "metadata": result.get("usage", {})}

    # ── Fix generation ────────────────────────────────────────────────────────

    async def generate_fix(
        self,
        vulnerability_type: str,
        severity: str,
        file_path: str,
        description: str,
        code_snippet: Optional[str] = None,
    ) -> Dict:
        """
        Returns dict with keys:
          suggested_fix  — human-readable description
          fixed_code     — actual replacement code (may equal suggested_fix as fallback)
          confidence     — float 0-1
          explanation    — why the fix works
        """
        snippet_block = ""
        if code_snippet and code_snippet.strip():
            snippet_block = f"\nVulnerable code:\n```\n{code_snippet.strip()[:600]}\n```\n"

        prompt = f"""You are a Python security expert. Fix this vulnerability.

Type: {vulnerability_type}
Severity: {severity}
File: {file_path}
Issue: {description}{snippet_block}

Reply with ONLY valid JSON — no markdown fences, no extra text:
{{"suggested_fix":"one sentence describing the fix","fixed_code":"the corrected replacement code","confidence":0.85,"explanation":"why this fix works"}}

IMPORTANT: fixed_code must be the actual corrected Python code that replaces the vulnerable snippet above. Never set it to null."""

        try:
            result = await self.generate(prompt)
            raw = result["response"].strip()
            logger.info(f"[openrouter] fix response for {vulnerability_type}: {raw[:200]}")

            fix_data = self._parse_json(raw)

            suggested = fix_data.get("suggested_fix") or description
            fixed     = fix_data.get("fixed_code")

            # Fallback: if model returned null/empty fixed_code, use suggested_fix
            if not fixed or not str(fixed).strip():
                logger.warning(f"[openrouter] fixed_code missing for {vulnerability_type}, using suggested_fix as fallback")
                fixed = suggested

            confidence = float(fix_data.get("confidence", 0.7))

            logger.info(f"[openrouter] ✅ fix generated — confidence={confidence:.2f}, fixed_code_len={len(str(fixed))}")

            return {
                "suggested_fix": suggested,
                "fixed_code":    str(fixed).strip(),
                "confidence":    confidence,
                "explanation":   fix_data.get("explanation", ""),
            }

        except Exception as e:
            logger.error(f"[openrouter] ❌ generate_fix failed for {vulnerability_type}: {e}")
            # Return a meaningful fallback so the scan still saves something
            fallback = f"# TODO: Fix {vulnerability_type} — {description}"
            return {
                "suggested_fix": f"Fix {vulnerability_type}: {description}",
                "fixed_code":    fallback,
                "confidence":    0.1,
                "explanation":   f"Auto-generated placeholder: {str(e)}",
            }

    # ── JSON parser ───────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON from model response, handling markdown fences."""
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find first {...} block
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass

        logger.warning(f"[openrouter] could not parse JSON from: {text[:200]}")
        return {}

    async def check_health(self) -> bool:
        try:
            if not self.api_key or self.api_key in ("", "your-openrouter-key", "your_private_key"):
                return False
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return resp.status_code == 200
        except Exception:
            return False
