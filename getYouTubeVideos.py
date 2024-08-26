import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

def getVideoLinksAndTitles(query):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = api_key

    youtube = build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.search().list(
        part="snippet",
        q=query
    )
    response = request.execute()

    results = []

    if response.get("items"):
        link = ""
        title = ""
        for item in response.get("items"):
            if item.get("id"):
                id = item.get("id")
                if id.get("videoId"):
                    # print("videoId: ", id.get("videoId"))
                    tlink = "https://www.youtube.com/watch?v=" + id.get("videoId")
                    # print("Link: ", tlink)
                if item.get("snippet"):
                    snippet = item.get("snippet")
                    if snippet.get("title"):
                        title = snippet.get("title")
                        link = tlink
                        # print("title: ", title)
                        results.append({
                            "title": title,
                            "link": link
                            })
                    else:
                        print("No title")
                else:
                    print("No snippet")
            else:
                print("No id")
    else:
        print("No items")

    return results
                    