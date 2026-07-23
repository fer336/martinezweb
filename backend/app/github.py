import httpx

from app.config import settings


async def trigger_deploy() -> None:
    url = (
        f"https://api.github.com/repos/{settings.github_repo}/actions/"
        f"workflows/{settings.github_workflow_file}/dispatches"
    )
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"ref": settings.github_ref})
        response.raise_for_status()
