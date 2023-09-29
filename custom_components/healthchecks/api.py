from typing import Literal, NotRequired, Union, assert_never
from urllib.parse import urljoin, urlparse, urlunsplit

import aiohttp
import async_timeout
from typing_extensions import TypedDict

Status = Literal["new", "up", "grace", "down", "paused"]
STATUSES: list[Status] = {
    "new",
    "up",
    "grace",
    "down",
    "paused",
}


class BaseCheck(TypedDict):
    name: str
    slug: str
    tags: str
    desc: str
    grace: int
    n_pings: int
    status: Status
    started: bool
    last_ping: str | None
    next_ping: str | None
    manual_resume: bool
    methods: str
    start_kw: str
    success_kw: str
    failure_kw: str
    filter_subject: bool
    filter_body: bool
    last_duration: NotRequired[int]


class BaseReadOnlyCheck(BaseCheck):
    unique_key: str


class SimpleReadOnlyCheck(BaseReadOnlyCheck):
    timeout: int


class CronReadOnlyCheck(BaseReadOnlyCheck):
    schedule: str
    tz: str


class BaseReadWriteCheck(BaseCheck):
    ping_url: str
    update_url: str
    pause_url: str
    resume_url: str
    channels: str


class SimpleReadWriteCheck(BaseReadWriteCheck):
    timeout: int


class CronReadWriteCheck(BaseReadWriteCheck):
    schedule: str
    tz: str


ReadOnlyCheck = Union[SimpleReadOnlyCheck, CronReadOnlyCheck]
ReadWriteCheck = Union[SimpleReadWriteCheck, CronReadWriteCheck]
Check = Union[ReadOnlyCheck, ReadWriteCheck]


class ListResponse(TypedDict):
    checks: list[Check]


class UnauthorizedError(Exception):
    "The API key is either missing or invalid."


async def check_api_key(
    session: aiohttp.ClientSession,
    api_url: str,
    api_key: str,
) -> bool:
    async with async_timeout.timeout(10):
        try:
            url = urljoin(api_url, "/api/v3/checks/")
            headers = {"X-Api-Key": api_key}
            response = await session.request(
                method="GET",
                url=url,
                headers=headers,
            )
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if response.status == 401:
                raise UnauthorizedError() from e
            else:
                raise e


async def list_checks(
    session: aiohttp.ClientSession,
    api_url: str,
    api_key: str,
    slug: str | None = None,
    tag: str | None = None,
) -> list[Check]:
    async with async_timeout.timeout(10):
        url = urljoin(api_url, "/api/v3/checks/")

        headers = {"X-Api-Key": api_key}

        params: dict[str, str] = {}
        if slug:
            params["slug"] = slug
        if tag:
            params["tag"] = tag

        response = await session.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
        )

        try:
            response.raise_for_status()
            data: ListResponse = await response.json()
            return data["checks"]
        except aiohttp.ClientResponseError as e:
            if response.status == 401:
                raise UnauthorizedError() from e
            else:
                raise e


def check_id(check: Check) -> str:
    if "ping_url" in check:
        return check_uuid(check)
    elif "unique_key" in check:
        return check["unique_key"]
    else:
        assert_never(check)


def check_uuid(check: BaseReadWriteCheck) -> str:
    uuid = check["ping_url"].split("/")[-1]
    assert len(uuid) == 36
    return uuid


def check_details_url(check: BaseReadWriteCheck) -> str:
    uri_components = urlparse(check["update_url"])
    scheme = uri_components.scheme
    netloc = uri_components.netloc

    uuid = uri_components.path.split("/")[-1]
    assert len(uuid) == 36
    path = f"/checks/{uuid}/details/"

    return urlunsplit((scheme, netloc, path, "", ""))


async def pause_check(
    session: aiohttp.ClientSession,
    check: ReadWriteCheck,
    api_key: str,
) -> None:
    async with async_timeout.timeout(10):
        url = check["pause_url"]
        headers = {"X-Api-Key": api_key}

        response = await session.request(
            method="POST",
            url=url,
            headers=headers,
        )

        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if response.status == 401 or response.status == 403:
                raise UnauthorizedError() from e
            else:
                raise e


async def resume_check(
    session: aiohttp.ClientSession,
    check: ReadWriteCheck,
    api_key: str,
) -> None:
    async with async_timeout.timeout(10):
        url = check["resume_url"]
        headers = {"X-Api-Key": api_key}

        response = await session.request(
            method="POST",
            url=url,
            headers=headers,
        )

        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if response.status == 401 or response.status == 403:
                raise UnauthorizedError() from e
            elif response.status == 409:
                # Ignore conflict errors
                return
            else:
                raise e


async def ping_check(
    session: aiohttp.ClientSession,
    check: ReadWriteCheck,
) -> None:
    async with async_timeout.timeout(10):
        response = await session.request(
            method="GET",
            url=check["ping_url"],
        )
        response.raise_for_status()
        assert response.status == 200
