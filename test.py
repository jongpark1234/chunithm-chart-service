from enum import Enum
import asyncio
import requests
import importlib.util
from http import HTTPStatus
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, cast
from zoneinfo import ZoneInfo
import aiohttp
from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from yarl import URL
from bs4.element import ResultSet, Tag

def extract_last_part(url: str) -> str:
    return url.split("_")[-1].split(".")[0]

def parse_player_rating(soup: ResultSet[Tag]) -> float:
    rating = ""
    for x in soup:
        digit = extract_last_part(cast(str, x["src"]))
        if digit == "comma":
            rating += "."
        else:
            rating += digit[1]
    return float(rating)

def chuni_int(s: str) -> int:
    return int(s.replace(",", ""))

def parse_time(time: str, format: str = "%Y/%m/%d %H:%M") -> datetime:
    return datetime.strptime(time, format).replace(tzinfo=ZoneInfo("Asia/Tokyo"))

class Possession(Enum):
    NONE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    RAINBOW = 4

    @classmethod
    def from_str(cls, s: str):
        if s == "silver":
            return cls.SILVER
        if s == "gold":
            return cls.GOLD
        if s == "platina" or s == "platinum":
            return cls.PLATINUM
        if s == "rainbow":
            return cls.RAINBOW

        return cls.NONE

    def color(self):
        match self.value:
            case 0:
                return 0xCECECE
            case 1:
                return 0x6BAAC7
            case 2:
                return 0xFCE620
            case 3:
                return 0xFFF6C5
            case 4:
                return 0x0B6FF3
            
class SkillClass(Enum):
    I = 1  # noqa: E741
    II = 2
    III = 3
    IV = 4
    V = 5
    INFINITE = 6

    def __str__(self):
        if self.value == 6:
            return "∞"
        return self.name

@dataclass
class Nameplate:
    content: str
    rarity: str


@dataclass
class Rating:
    current: float
    max: Optional[float] = None


@dataclass
class Currency:
    owned: int
    total: int


@dataclass
class Overpower:
    value: float
    progress: float


@dataclass(kw_only=True)
class UserAvatar:
    base: str
    back: str
    skinfoot_r: str
    skinfoot_l: str
    skin: str
    wear: str
    face: str
    face_cover: str
    head: str
    hand_r: str
    hand_l: str
    item_r: str
    item_l: str


@dataclass(kw_only=True)
class Team:
    # emblem: some_enum_here
    name: str
@dataclass(kw_only=True)
class PlayerData:
    possession: Possession = Possession.NONE

    character: Optional[str] = None
    avatar: UserAvatar

    name: str

    reborn: int = 0
    lv: int

    playcount: Optional[int] = None
    last_play_date: datetime

    team: Optional[Team] = None
    overpower: Overpower
    nameplate: Nameplate
    rating: Rating
    currency: Optional[Currency] = None

    friend_code: Optional[str] = None

    emblem: Optional[SkillClass] = None
    medal: Optional[SkillClass] = None
    
    

def parse_player_card_and_avatar(soup: BeautifulSoup):
    if (e := soup.select_one(".player_chara img")) is not None:
        character = cast(str, e["src"])
    else:
        character = None

    name = soup.select_one(".player_name_in").get_text()
    lv = chuni_int(soup.select_one(".player_lv").get_text())

    team_name_elem = soup.select_one(".player_team_name")
    team_name = team_name_elem.get_text() if team_name_elem else None

    nameplate_content = soup.select_one(".player_honor_text").get_text()
    nameplate_rarity = (
        str(soup.select_one(".player_honor_short")["style"])
        .split("_")[-1]
        .split(".")[0]
    )

    rating = parse_player_rating(soup.select(".player_rating_num_block img"))
    max_rating = float(soup.select_one(".player_rating_max").get_text())

    overpower = soup.select_one(".player_overpower_text").get_text().split(" ")
    overpower_value = float(overpower[0])
    overpower_progress = (
        float(overpower[1].replace("(", "").replace(")", "").replace("%", "")) / 100
    )

    last_play_date_str = soup.select_one(".player_lastplaydate_text").get_text()
    last_play_date = parse_time(last_play_date_str)

    reborn_elem = soup.select_one(".player_reborn")
    reborn = chuni_int(reborn_elem.get_text()) if reborn_elem else 0

    possession_elem = soup.select_one(".box_playerprofile")
    possession = (
        Possession.from_str(extract_last_part(possession_elem["style"]))  # type: ignore[reportGeneralTypeIssues]
        if possession_elem and possession_elem.has_attr("style")
        else Possession.NONE
    )

    classemblem_base_elem = soup.select_one(".player_classemblem_base img")
    emblem = (
        SkillClass(
            chuni_int(extract_last_part(classemblem_base_elem["src"]))  # type: ignore[reportGeneralTypeIssues]
        )
        if classemblem_base_elem and classemblem_base_elem.has_attr("src")
        else None
    )

    classemblem_top_elem = soup.select_one(".player_classemblem_top img")
    medal = (
        SkillClass(
            chuni_int(extract_last_part(classemblem_top_elem["src"]))  # type: ignore[reportGeneralTypeIssues]
        )
        if classemblem_top_elem and classemblem_top_elem.has_attr("src")
        else None
    )

    avatar_group = soup.select_one(".avatar_group")
    avatar = UserAvatar(
        base="https://new.chunithm-net.com/chuni-mobile/html/mobile/images/avatar_base.png",
        back=cast(str, avatar_group.select_one(".avatar_back img")["src"]),
        skinfoot_r=cast(str, avatar_group.select_one(".avatar_skinfoot_r img")["src"]),
        skinfoot_l=cast(str, avatar_group.select_one(".avatar_skinfoot_l img")["src"]),
        skin=cast(str, avatar_group.select_one(".avatar_skin img")["src"]),
        wear=cast(str, avatar_group.select_one(".avatar_wear img")["src"]),
        face=cast(str, avatar_group.select_one(".avatar_face img")["src"]),
        face_cover=cast(str, avatar_group.select_one(".avatar_faceCover img")["src"]),
        head=cast(str, avatar_group.select_one(".avatar_head img")["src"]),
        hand_r=cast(str, avatar_group.select_one(".avatar_hand_r img")["src"]),
        hand_l=cast(str, avatar_group.select_one(".avatar_hand_l img")["src"]),
        item_r=cast(str, avatar_group.select_one(".avatar_item_r img")["src"]),
        item_l=cast(str, avatar_group.select_one(".avatar_item_l img")["src"]),
    )

    return PlayerData(
        character=character,
        avatar=avatar,
        name=name,
        lv=lv,
        reborn=reborn,
        possession=possession,
        team=Team(name=team_name) if team_name else None,
        nameplate=Nameplate(content=nameplate_content, rarity=nameplate_rarity),
        rating=Rating(rating, max_rating),
        overpower=Overpower(overpower_value, overpower_progress),
        last_play_date=last_play_date,
        emblem=emblem,
        medal=medal,
    )
    
    
    
    
    
__all__ = ['ChuniNet']

class ChuniNet:
    AUTH_URL = "https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/"

    def __init__(
        self,
        clal: str,
        *,
        user_id: Optional[str] = None,
        token: Optional[str] = None,
        base: Optional[URL] = None,
    ) -> None:
        if base is None:
            self.base = URL("https://chunithm-net-eng.com")
        else:
            self.base = base
        self.clal = clal

        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())
        self.session.cookie_jar.update_cookies(
            {"clal": clal}, URL("https://lng-tgk-aime-gw.am-all.net")
        )

        self.bs4_features = (
            "lxml" if importlib.util.find_spec("lxml") else "html.parser"
        )

        if user_id is not None:
            self.session.cookie_jar.update_cookies({"userId": user_id}, self.base)
        if token is not None:
            self.session.cookie_jar.update_cookies({"_t": token}, self.base)

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.session.close()

    async def close(self):
        await self.session.close()

    @property
    def user_id(self):
        cookie = self.session.cookie_jar.filter_cookies(self.base).get("userId")
        if cookie is None:
            return None
        return cookie.value

    @property
    def token(self):
        cookie = self.session.cookie_jar.filter_cookies(self.base).get("_t")
        if cookie is None:
            return None
        return cookie.value

    def clear_cookies(self):
        self.session.cookie_jar.clear_domain(self.base.host or "chunithm-net-eng.com")

    async def validate_cookie(self):
        async with self.session.get(self.AUTH_URL, allow_redirects=False) as req:
            if req.status != HTTPStatus.FOUND:
                msg = f"Invalid cookie. Received status code was {req.status}"
                raise Exception(msg)
            return req.headers["Location"]

    async def authenticate(self) -> "PlayerData":
        if self.user_id is not None:
            try:
                # In some cases, the site token is refreshed automatically.
                resp = await self._request("mobile/home/")
            except Exception as e:
                # In other cases, the token is invalidated and a relogin is required.
                # Error code for when site token is invalidated
                if e.code != 200004:
                    raise
                uid_redemption_url = await self.validate_cookie()
                resp = await self.session.get(uid_redemption_url)
        else:
            uid_redemption_url = await self.validate_cookie()
            resp = await self.session.get(uid_redemption_url)

        if resp.status == HTTPStatus.SERVICE_UNAVAILABLE:
            msg = "Service under maintenance"
            raise Exception(msg)
        if self.session.cookie_jar.filter_cookies(self.base).get("userId") is None:
            msg = "Invalid cookie: No userId cookie found"
            raise Exception(msg)

        return parse_player_card_and_avatar(
            BeautifulSoup(await resp.text(), self.bs4_features)
        )

    async def _request(self, endpoint: str, method="GET", **kwargs) -> "ClientResponse":
        if self.user_id is None:
            await self.authenticate()

        response = await self.session.request(method, self.base / endpoint, **kwargs)
        # We could be here because the client attempted to reauthenticate
        # but the clal was invalid.
        if response.url.path == "/mobile/" and self.AUTH_URL in (await response.text()):
            self.clear_cookies()
            await self.authenticate()
            return await self._request(endpoint, method, **kwargs)

        if response.url.path.startswith("/mobile/error"):
            soup = BeautifulSoup(await response.text(), self.bs4_features)
            err = soup.select(".block.text_l .font_small")

            errcode = int(err[0].get_text().split(":")[1])
            description = err[1].get_text() if len(err) > 1 else ""
            raise Exception(errcode, description)

        return response

    async def player_data(self):
        resp = await self._request("mobile/home/playerData")
        soup = BeautifulSoup(await resp.text(), self.bs4_features)
        return soup.get_text()
    
async def player_data():
    chuninet = ChuniNet('b41f7db64b7b513cac2119cf022dc7ff')
    resp = await chuninet._request("mobile/home/playerData")
    soup = BeautifulSoup(await resp.text(), "lxml" if importlib.util.find_spec("lxml") else "html.parser")
    print(soup.get_text())
    
asyncio.run(player_data())








#  if code is not None:
#             self.script = "javascript:void(function(d){var s=d.createElement('script');s.src='https://gistcdn.githack.com/beerpiss/0eb8d3e50ae753388a6d4a4af5678a2e/raw/70f4e2f4defb26eb053b68dcee8c6250ba178503/login.js' ;d.body.append(s)}(document))\n"
#         else:
#             self.script = "javascript:void(function(d){var s=d.createElement('script');s.src='https://gistcdn.githack.com/beerpiss/0eb8d3e50ae753388a6d4a4af5678a2e/raw/c096f619a3a207b99a0cbb63e1d214a7b1af4f28/login2.js' ;d.body.append(s)}(document))\n"

#         items = [
#             (
#                 "**Step 1:**\n"
#                 "Log into [CHUNITHM-NET](https://chunithm-net-eng.com) in an incognito/private window.\n"
#                 "(right click and copy link on desktop, long press and copy link on mobile)"
#             ),
#             (
#                 "**Step 2**:\n"
#                 f"Copy [this link](https://lng-tgk-aime-gw.am-all.net/common_auth/{f'#{code}' if code is not None else ''}) and paste it in the current incognito window.\n"
#                 'The website should display "Not Found".'
#             ),
#             (
#                 "**Step 3**:\n\n"
#                 "**Desktop users:**\n"
#                 "Copy the script above and paste it in your browser's developer console (Ctrl + Shift + I or F12).\n\n"
#                 "**Mobile users:**\n"
#                 '1. Long press the message above and select "Copy Text".\n'
#                 "2. Create a bookmark in your browser and paste the copied text in the URL field.\n"
#                 "3. Run the bookmark.\n\n"
#                 "This script cannot access your Aime account! It can only access CHUNITHM-NET.\n"
#                 "\n"
#             ),
#         ]

#            "The website will display the login command. Copy it and paste it in the bot's DMs."
#             f"If the website asks for a passcode, enter **{code}** and select OK."