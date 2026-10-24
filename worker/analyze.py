"""Analyze stage: extracts repository AST/README and synthesizes structured ProductBrief."""

import json
import re
import httpx
from api.config import settings
from worker.models import FeatureItem, MetricItem, ProductBrief

GITHUB_API_BASE = "https://api.github.com/repos"

def parse_github_owner_repo(repo_url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    clean = re.sub(r"^(https?://)?(www\.)?github\.com/", "", repo_url).strip("/")
    parts = clean.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    return parts[0], parts[1].replace(".git", "")

async def fetch_github_data(repo_url: str) -> dict:
    """Fetch README, package.json, and file tree from GitHub API or raw content."""
    owner, repo = parse_github_owner_repo(repo_url)
    headers = {"User-Agent": "Premiere-Pipeline"}
    data = {"readme": "", "package_json": {}, "routes": ["/"]}

    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        # 1. Fetch README.md
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
        r = await client.get(readme_url)
        if r.status_code != 200:
            r = await client.get(f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md")
        if r.status_code == 200:
            data["readme"] = r.text[:6000]

        # 2. Fetch package.json
        pkg_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/package.json"
        pkg_r = await client.get(pkg_url)
        if pkg_r.status_code == 200:
            try:
                data["package_json"] = pkg_r.json()
            except Exception:
                pass

        # 3. Detect routes from git tree
        tree_url = f"{GITHUB_API_BASE}/{owner}/{repo}/git/trees/main?recursive=1"
        tree_r = await client.get(tree_url)
        if tree_r.status_code == 200:
            tree_data = tree_r.json()
            routes = set(["/"])
            for item in tree_data.get("tree", []):
                path = item.get("path", "")
                if ("pages/" in path or "app/" in path) and any(path.endswith(ext) for ext in [".tsx", ".jsx", ".vue"]):
                    cleaned = re.sub(r"^(pages|app)/?", "/", path)
                    cleaned = re.sub(r"/(page|index)\.[a-z]+$", "", cleaned)
                    cleaned = re.sub(r"\.[a-z]+$", "", cleaned)
                    if cleaned and not cleaned.startswith("/api") and "[" not in cleaned:
                        routes.add(cleaned)
            data["routes"] = sorted(list(routes))[:5]

    return data

def build_deterministic_brief(repo_url: str, live_url: str, data: dict) -> ProductBrief:
    """Deterministic fallback brief generator when LLM API keys are not supplied."""
    owner, repo = parse_github_owner_repo(repo_url)
    clean_name = repo.replace("-", " ").replace("_", " ").title()
    pkg = data.get("package_json", {})
    desc = pkg.get("description") or "High performance software engineered for modern workflows."

    return ProductBrief(
        product_name=clean_name,
        tagline="ENGINEERED FOR UNCOMPROMISING SPEED",
        elevator_pitch=desc,
        primary_audience="Engineers, creators, and modern product teams",
        category="SaaS Platform",
        key_features=[
            FeatureItem(headline="AUTONOMOUS PIPELINE", detail="Instant workflow automation from source to delivery", associated_route="/"),
            FeatureItem(headline="REAL-TIME TELEMETRY", detail="Sub-millisecond state tracking and live telemetry", associated_route=data["routes"][1] if len(data["routes"]) > 1 else "/"),
            FeatureItem(headline="SCALABLE ARCHITECTURE", detail="Built for enterprise workloads and instant scaling", associated_route="/"),
        ],
        metrics=[
            MetricItem(value="10x", label="FASTER EXECUTION"),
            MetricItem(value="99.9%", label="PIPELINE UPTIME"),
            MetricItem(value="<5ms", label="QUERY LATENCY"),
        ],
        detected_routes=data.get("routes", ["/"]),
        brand_color="#3B82F6",
    )

async def analyze_repository(repo_url: str, live_url: str) -> ProductBrief:
    """Main analyze stage entrypoint returning validated ProductBrief."""
    repo_data = await fetch_github_data(repo_url)

    # If OpenAI API key is set, call LLM; otherwise use deterministic fallback
    if settings.openai_api_key and settings.llm_provider == "openai":
        try:
            prompt = (
                f"Extract structured product launch brief from GitHub repo:\n"
                f"README snippet: {repo_data['readme'][:2000]}\n"
                f"Package info: {json.dumps(repo_data['package_json'])}\n"
                f"Detected routes: {repo_data['routes']}\n"
                f"Format as JSON conforming to: product_name, tagline (max 6 uppercase words), "
                f"elevator_pitch, primary_audience, category, key_features (list with headline, detail, associated_route), "
                f"metrics (list with value, label), detected_routes, brand_color"
            )
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={
                        "model": "gpt-4o",
                        "response_format": {"type": "json_object"},
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                if res.status_code == 200:
                    payload = res.json()["choices"][0]["message"]["content"]
                    return ProductBrief.model_validate_json(payload)
        except Exception:
            # Fall back to deterministic on any LLM parsing or network issue
            pass

    return build_deterministic_brief(repo_url, live_url, repo_data)
