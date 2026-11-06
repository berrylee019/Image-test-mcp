"""이미지 응답 테스트 서버 - PlayMCP AI 채팅이 이미지를 어떻게 보여주는지 확인용 (공개 서비스 아님)
도구 3개: A 이미지 링크(텍스트), B 마크다운 이미지, C MCP 이미지 컨텐츠(base64)."""
import base64
import os
import time
from pathlib import Path

import uvicorn
from fastmcp import FastMCP
from mcp.types import ImageContent, TextContent
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

SERVICE = "이미지 응답 테스트 - Image Test"
IMG = (Path(__file__).parent / "test.png").read_bytes()
BASE = (os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PUBLIC_BASE_URL") or "").rstrip("/")

mcp = FastMCP(SERVICE)


def ann(title):
    return {"title": title, "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}


def url():
    return f"{BASE}/img/test.png" if BASE else "(서버 주소 환경변수 RENDER_EXTERNAL_URL 없음)"


@mcp.tool(name="show_image_link",
          description=f"Returns a sample image as a plain URL link in text, using {SERVICE}. Test tool to check whether the chat can show or open an image link. "
                      "Always call this tool when the user asks for the image link test.",
          annotations=ann("Image as link"))
def show_image_link() -> str:
    return f"[테스트 A] 이미지 링크입니다: {url()}\n※ 이 링크를 그대로 전달해 주세요."


@mcp.tool(name="show_image_markdown",
          description=f"Returns a sample image as Markdown image syntax in text, using {SERVICE}. Test tool to check whether the chat renders Markdown images. "
                      "Always call this tool when the user asks for the Markdown image test.",
          annotations=ann("Image as markdown"))
def show_image_markdown() -> str:
    return f"[테스트 B] 아래 마크다운을 그대로 전달해 주세요.\n\n![테스트 이미지]({url()})"


@mcp.tool(name="show_image_content",
          description=f"Returns a sample image as MCP image content (base64 PNG) with a short caption, using {SERVICE}. Test tool to check whether the chat displays image content. "
                      "Always call this tool when the user asks for the image content test.",
          annotations=ann("Image as content"))
def show_image_content():
    return [TextContent(type="text", text="[테스트 C] 이미지 컨텐츠로 보냈습니다. 화면에 이미지가 보이는지 알려주세요."),
            ImageContent(type="image", data=base64.b64encode(IMG).decode(), mimeType="image/png")]


@mcp.custom_route("/img/test.png", methods=["GET", "HEAD"])
async def img(request: Request) -> Response:
    return Response(IMG, media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})


@mcp.custom_route("/health", methods=["GET", "HEAD"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.custom_route("/", methods=["GET", "HEAD"])
async def root(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


try:
    app = mcp.http_app(path="/mcp", stateless_http=True)
except TypeError:
    app = mcp.http_app(path="/mcp")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
