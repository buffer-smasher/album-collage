from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import requests
import spotipy
import random
import os

load_dotenv()

CLIENT_ID = os.getenv("CILENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_tracks_from_playlist(playlist_id):
    tracks_response = sp.playlist_tracks(playlist_id)
    playlist_data = tracks_response["items"]
    while tracks_response["next"]:
        tracks_response = sp.next(tracks_response)
        playlist_data.extend(tracks_response["items"])

    # album url: playlist_data[trackindex]["track"]["album"]["external_urls"]["spotify"]
    # iamge url: playlist_data[trackindex]["track"]["album"]["images"][1]["url"]
    return playlist_data


def sort_albums(playlist_data):
    raw_album_list = []
    for album in playlist_data:
        raw_album_list.append(album["track"]["album"]["external_urls"]["spotify"])

    album_count = {}
    for album in raw_album_list:
        album_count[album] = raw_album_list.count(album)

    # returns list ordered by most occurences
    return sorted(album_count, key=album_count.get, reverse=True)


def get_cover_images(playlist_data, album_list):
    image_list = []
    for album_url in album_list:
        for track in playlist_data:
            if track["track"]["album"]["external_urls"]["spotify"] == album_url:
                image_url = track["track"]["album"]["images"][1]["url"]
                if not image_url in image_list:
                    image_list.append(image_url)
    return image_list


def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def create_collage(image_list, output_path, grid_size=(3, 3)):
    # Initialize collage size based on the number of rows and columns
    collage_width = 0
    collage_height = 0

    # Calculate the size of each cell in the collage
    for i in range(min(len(image_list), grid_size[0])):
        img = load_image(image_list[i])
        collage_width += img.width

    for j in range(min(len(image_list), grid_size[1])):
        img = load_image(image_list[j])
        collage_height += img.height

    # Create the collage with dynamically calculated size
    collage = Image.new("RGB", (collage_width, collage_height))

    # Coordinates to keep track of where to paste the next image
    x_offset = 0
    y_offset = 0

    # Iterate through the cells and paste images
    for i in range(min(len(image_list), grid_size[0])):
        for j in range(min(len(image_list), grid_size[1])):
            img = load_image(image_list.pop(0))
            collage.paste(img, (x_offset, y_offset))
            x_offset += img.width

        x_offset = 0
        y_offset += img.height

    # Save the collage
    collage.save(output_path)
    collage.show()


playlist_data = get_tracks_from_playlist("1Hb86FTOjUPg0AaKAOPTq8")
album_list = sort_albums(playlist_data)
cover_images = get_cover_images(playlist_data, album_list)

create_collage(
    image_list=cover_images,
    output_path="test.png",
    grid_size=(26, 14),
)
