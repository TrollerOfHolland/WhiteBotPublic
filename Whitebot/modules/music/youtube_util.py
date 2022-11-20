from youtubesearchpython import VideosSearch
from modules.music.tune import Tune


def youtube_search(query, lim: int = 1) -> list[Tune]:
    search = VideosSearch(query, limit=lim)
    result_tunes = []
    for result in search.result()['result']:
        result_tunes.append(Tune(result))
    return result_tunes


def get_youtube_url(query) -> Tune:
    parsed_results = youtube_search(query)
    return parsed_results[0] if parsed_results else None
