import asyncio
from typing import Optional
from ebooklib import epub
import unicodedata
import re
import backoff
from aiohttp import ClientResponseError, ClientSession
from aiohttp_client_cache import FileBackend
from bs4 import BeautifulSoup
from json import loads
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

cache = FileBackend(use_temp=True, expire_after=43200)  # 12 hours

# --- Utilities --- #


async def wp_get_cookies(username: str, password: str) -> dict:
    # source: https://github.com/TheOnlyWayUp/WP-DM-Export/blob/dd4c7c51cb43f2108e0f63fc10a66cd24a740e4e/src/API/src/main.py#L25-L58
    """Retrieves authorization cookies from Inkitt by logging in with user creds.

    Args:
        username (str): Username.
        password (str): Password.

    Raises:
        ValueError: Bad status code.
        ValueError: No cookies returned.

    Returns:
        dict: Authorization cookies.
    """
    try:
    # Inkitt login credentials are stored at "./inkitt_credentials"
    # The format is "{"email":"{email}","password":"{password}"}"
        file = open("./inkitt_credentials", "r")
        credentials = loads(file.read())
        file.close
    except ValueError:
        print("Incorrect Inkitt login info format")
    except FileNotFoundError:
        print("There is no inkitt_credentials file")
        credentials=loads("{\"email\":\"\",\"password\":\"\"}")
        credentials["email"]=username
        credentials["password"]=password

    async with ClientSession(headers=headers) as session:
        async with session.post(
            "https://www.inkitt.com/api/login", json=credentials
        ) as response:
            if response.status != 200:
                print(response.status)
                raise ValueError("Not a 200.")

            cookies = {
                k: v.value
                for k, v in response.cookies.items()  # Thanks https://stackoverflow.com/a/32281245
            }

            if not cookies:
                raise ValueError("No cookies.")

            return cookies

def slugify(value, allow_unicode=False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    Thanks https://stackoverflow.com/a/295466.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


# --- API Calls --- #


@backoff.on_exception(backoff.expo, ClientResponseError, max_time=15)
async def retrieve_story(story_id: int, cookies: dict = None) -> dict:
    """Taking a story_id, return its information from the Inkitt API."""
    async with (
        ClientSession(headers=headers, cookies=cookies)
    ) as session:
        async with session.get(
            f"https://www.inkitt.com/api/stories/{story_id}"
        ) as response:
            if not response.ok:
                if response.status in [404, 400]:
                    return {}
            response.raise_for_status()

            body = await response.json()
    return body


@backoff.on_exception(backoff.expo, ClientResponseError, max_time=15)
async def fetch_part_content(url: str, cookies: dict = None) -> str:
    """Return the HTML Content of a Part."""
    async with (
        ClientSession(headers=headers, cookies=cookies)
    ) as session:  # Don't cache requests with Cookies.
        async with session.get(
            url
        ) as response:
            if not response.ok:
                if response.status in [404, 400]:
                    return ""
            response.raise_for_status()

            body = await response.text()
    body = body[body.find("<p data-content") :]
    body = body[: body.find("</div>") - 2]
    print(body)
    return body


@backoff.on_exception(backoff.expo, ClientResponseError, max_time=15)
async def fetch_cover(url: str, cookies: Optional[dict] = None) -> bytes:
    """Fetch image bytes."""
    async with (
        CachedSession(headers=headers, cache=cache)
        if not cookies
        else ClientSession(headers=headers, cookies=cookies)
    ) as session:  # Don't cache requests with Cookies.
        async with session.get(url) as response:
            if not response.ok:
                if response.status in [404, 400]:
                    return bytes()
            response.raise_for_status()

            body = await response.read()

    return body


# --- EPUB Generation --- #


def set_metadata(book, data):
    book.add_author(data["user"]["username"])

    #book.add_metadata("DC", "description", data["description"])
    #book.add_metadata("DC", "created", data["createDate"])
    #book.add_metadata("DC", "modified", data["modifyDate"])
    book.add_metadata("DC", "language", data["language"]["locale"])

    # book.add_metadata(
    #     None, "meta", "", {"name": "tags", "content": ", ".join(data["content_labels"])}
    # )
    # book.add_metadata(
    #     None, "meta", "", {"name": "mature", "content": str(int(data["mature"]))}
    # )
    # book.add_metadata(
    #     None, "meta", "", {"name": "completed", "content": str(int(data["completed"]))}
    # )


async def set_cover(book, data, cookies: Optional[dict] = None):
    book.set_cover("cover.jpg", await fetch_cover(data["vertical_cover"]["url"], cookies=cookies))


async def add_chapters(
    book, data, download_images: bool = False, cookies: dict = None
):
    chapters = []

    for cidx, chapter in enumerate(data["chapters"]):
        url = (
            "https://inkitt.com/stories/"
            + str(data["category_one"])
            + "/"
            + str(data["id"])
            + "/chapters/"
            + str(chapter["chapter_number"])
        )
        content = await fetch_part_content(url, cookies=cookies)
        title = chapter["name"]
        clean_title = slugify(title)

        # Thanks https://eu17.proxysite.com/process.php?d=5VyWYcoQl%2BVF0BYOuOavtvjOloFUZz2BJ%2Fepiusk6Nz7PV%2B9i8rs7cFviGftrBNll%2B0a3qO7UiDkTt4qwCa0fDES&b=1
        chapter = epub.EpubHtml(
            title=title,
            file_name=f"{cidx}.xhtml",  # Used to be clean_title.xhtml, but that broke Arabic support as slugify turns arabic strings into '', leading to multiple files with the same name, breaking those chapters.
            lang=data["language"]["locale"],
        )

        # if download_images:
        #     soup = BeautifulSoup(content, "lxml")
        #     async with (
        #         CachedSession(headers=headers, cache=cache)
        #         if not cookies
        #         else ClientSession(headers=headers, cookies=cookies)
        #     ) as session:  # Don't cache requests with Cookies.
        #         for idx, image in enumerate(soup.find_all("img")):
        #             if not image["src"]:
        #                 continue
        #             async with session.get(image["src"]) as response:
        #                 img = epub.EpubImage(
        #                     media_type="image/jpeg",
        #                     content=await response.read(),
        #                     file_name=f"static/{cidx}/{idx}.jpeg",
        #                 )
        #                 book.add_item(img)
        #                 content = content.replace(
        #                     str(image), f'<img src="static/{cidx}/{idx}.jpeg"/>'
        #                 )

        chapter.set_content(f"<h1>{title}</h1>" + content)

        chapters.append(chapter)

        yield title  # Yield the chapter's title upon insertion preceeded by retrieval.

    for chapter in chapters:
        book.add_item(chapter)

    book.toc = tuple(chapters)

    # Thanks https://github.com/aerkalov/ebooklib/blob/master/samples/09_create_image/create.py
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # create spine
    book.spine = ["nav"] + chapters
