import asyncio
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional, Tuple
import httpx
from app.domain.enums import FetchStatus, SourceType
from app.tools.extractors import classify_source_url, extract_html_text, extract_pdf_text

class FetchResult:
    # Encapsulates result and extracted text of a fetched URL
    def __init__(
        self,
        url: str,
        status: FetchStatus,
        source_type: SourceType,
        text_content: str = "",
        http_status: Optional[int] = None,
        error: Optional[str] = None,
    ):
        self.url = url
        self.status = status
        self.source_type = source_type
        self.text_content = text_content
        self.http_status = http_status
        self.error = error

def validate_ssrf_safety(url: str) -> Tuple[bool, Optional[str]]:
    # Validate URL against SSRF attacks by inspecting resolved IPs
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Malformed URL"

    if parsed.scheme not in ("http", "https"):
        return False, "Unsupported URL scheme"

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname"

    # Block localhost or link-local string identifiers
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        return False, "Access to localhost or internal hosts is forbidden"

    try:
        # Resolve all IPv4 and IPv6 addresses for hostname
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)

            # Block private, loopback, link-local, or cloud metadata addresses
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_str.startswith("169.254.")
            ):
                return False, f"Blocked private or restricted IP target: {ip_str}"

    except socket.gaierror:
        return False, "DNS resolution failed for hostname"
    except Exception as e:
        return False, f"SSRF validation error: {e}"

    return True, None

async def fetch_page_content(
    url: str,
    max_retries: int = 2,
    max_body_bytes: int = 5 * 1024 * 1024,
) -> FetchResult:
    # Fetch URL safely with SSRF protection, size caps, and text extraction
    source_type = classify_source_url(url)

    is_safe, ssrf_error = validate_ssrf_safety(url)
    if not is_safe:
        return FetchResult(
            url=url,
            status=FetchStatus.BLOCKED,
            source_type=source_type,
            error=ssrf_error,
        )

    headers = {
        "User-Agent": "ScholarPilot/1.0 (+https://scholarpilot.ai; Academic Research)",
        "Accept-Language": "en, *;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
    }

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            timeout = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, max_redirects=3) as client:
                response = await client.get(url, headers=headers)

                # Handle rate limiting with Retry-After header
                if response.status_code == 429:
                    retry_after_str = response.headers.get("Retry-After", "3")
                    try:
                        wait_s = min(float(retry_after_str), 15.0)
                    except ValueError:
                        wait_s = 3.0
                    await asyncio.sleep(wait_s)
                    continue

                if response.status_code >= 500:
                    last_error = f"HTTP server error status {response.status_code}"
                    await asyncio.sleep((attempt + 1) * 1.5)
                    continue

                if response.status_code != 200:
                    return FetchResult(
                        url=url,
                        status=FetchStatus.FAILED,
                        source_type=source_type,
                        http_status=response.status_code,
                        error=f"HTTP status {response.status_code}",
                    )

                content_bytes = response.content
                if len(content_bytes) > max_body_bytes:
                    content_bytes = content_bytes[:max_body_bytes]

                content_type = response.headers.get("Content-Type", "").lower()

                # Process PDF or HTML text
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    extracted_text = extract_pdf_text(content_bytes)
                else:
                    text_body = content_bytes.decode("utf-8", errors="replace")
                    extracted_text = extract_html_text(text_body)

                if not extracted_text:
                    return FetchResult(
                        url=url,
                        status=FetchStatus.PARSE_FAILED,
                        source_type=source_type,
                        http_status=response.status_code,
                        error="No readable text content extracted from page",
                    )

                return FetchResult(
                    url=url,
                    status=FetchStatus.OK,
                    source_type=source_type,
                    text_content=extracted_text,
                    http_status=response.status_code,
                )

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            last_error = str(e)
            await asyncio.sleep((attempt + 1) * 1.5)
        except Exception as e:
            return FetchResult(
                url=url,
                status=FetchStatus.FAILED,
                source_type=source_type,
                error=str(e),
            )

    return FetchResult(
        url=url,
        status=FetchStatus.FAILED,
        source_type=source_type,
        error=f"Exhausted retries. Last error: {last_error}",
    )
