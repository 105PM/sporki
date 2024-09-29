from .setup import P
from support import d, default_headers, logger
from tool import ToolUtil
import requests, json


class Sporki:
    @classmethod
    def ch_list(cls):
        channels = list()

        global_data = requests.get(
            "https://api.sporki.com/display/v1/home/global", headers=default_headers
        ).json()
        tv_data = list(
            filter(
                lambda x: x["moduleType"]["code"] == 22,
                global_data["result"]["homeDisplay"],
            )
        )[0]["item"]
        # live_data = list(
        #     filter(
        #         lambda x: x["moduleType"]["code"] == 10,
        #         global_data["result"]["homeDisplay"],
        #     )
        # )[0]

        for x in tv_data:
            url = (
                f"https://api.sporki.com/sports/v1{x['linkUrl'].split('sporki.com')[1]}"
            )
            ch_info = requests.get(url, headers=default_headers).json()["result"]

            entity = {
                "type": "tv",
                "name": ch_info["broadcast"][0]["channelName"],
                "current": ch_info["gameTitle"],
                "category": ch_info["sportsCodeName"],
                "url": ch_info["broadcast"][0]["channelUrl"],
                "id": ch_info["seq"]
            }
            channels.append(entity)

        # live_video = list(
        #     filter(lambda x: x["broadcastType"]["code"] == 1 and x["gameStatus"]["code"] == 2, live_data["item"])
        # )

        # for x in live_video:
        #     url = f"https://api.sporki.com/sports/v1/{x['sportsCodeValue']}/game/{x['seq']}"
        #     game_info = requests.get(url, headers=default_headers).json()["result"]

        #     entity = {
        #         "type": "live",
        #         "name": game_info["broadcast"][0]["channelName"],
        #         "current": f'[{game_info["leagueCodeName"]}] {game_info["gameTitle"]}',
        #         "category": game_info["sportsCodeName"],
        #         "url": game_info["broadcast"][0]["channelUrl"],
        #         "id": game_info["seq"]
        #     }
        #     channels.append(entity)

        # P.logger.debug(channels)

        return channels
    
    @classmethod
    def get_m3u8(cls, ch_id):
        ch_list = cls.ch_list()
        ch = list(filter(lambda x:x['id'] == int(ch_id), ch_list))[0]

        return 'redirect', ch['url']

    @classmethod
    def make_m3u(cls):
        M3U_FORMAT = '#EXTINF:-1 tvg-id=\"{id}\" tvg-name=\"{title}\" group-title=\"{group}\" tvg-chno=\"{ch_no}\" tvh-chnum=\"{ch_no}\",{title}\n{url}\n' 
        m3u = '#EXTM3U\n'
        for idx, item in enumerate(cls.ch_list()):
            if item['type'] == 'tv':
                m3u += M3U_FORMAT.format(
                    id=item['id'],
                    title=item['name'],
                    group=item['category'],
                    ch_no=str(idx+1),
                    url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['id']}"),
                )
            elif item['type'] == 'live':
                m3u += M3U_FORMAT.format(
                    id=item['id'],
                    title=f"{item['current']} ({item['name']})",
                    group=item['category'],
                    ch_no=str(idx+1),
                    url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['id']}"),
                )
        return m3u
