import asyncio
import time
from pathlib import Path

from httpx import AsyncClient

BASE_URL = "http://mp.ituring.com.cn/files/flags"
DEST_DIR = Path("downloads")


def save_flag(image: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(image)


async def get_flag(client: AsyncClient, cc: str) -> bytes:
    url = f"{BASE_URL}/{cc}/{cc}.gif".lower()
    resp = await client.get(url, timeout=5.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


async def download_one(client: AsyncClient, cc: str) -> bytes:
    image = await get_flag(client, cc)
    save_flag(image, f"{cc}.gif")


async def supervisor(cc_list: list[str]) -> int:
    async with AsyncClient() as client:
        download_coros = [download_one(client, cc) for cc in cc_list]
        res = await asyncio.gather(*download_coros)
        return len(res)


def download_many(cc_list: list[str]) -> int:
    return asyncio.run(supervisor(cc_list))


def main(downloader):
    cc_list = "CH IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR".split()
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(cc_list)
    elapsed = time.perf_counter() - t0
    print(f"\n{count} downloads in {elapsed: .4f}s")


if __name__ == "__main__":
    main(download_many)
