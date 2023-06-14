# based on 
# https://github.com/isaackogan/TikTokLive
# this to simulate the chat Reader Example.
# you can adjust the script as you need..
# author : puremindforever
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, LiveEvent, LikeEvent
import io
import tkinter as tk
from PIL import ImageTk, Image
import pygame
import threading
import queue

# intiate pygame for playing sounds.
pygame.init()
sambosa_sound = pygame.mixer.Sound("waves/sa.wav")
n3na3_sound = pygame.mixer.Sound("waves/n3.wav")
kabso_sound = pygame.mixer.Sound("waves/ka.wav")
hadeda_sound = pygame.mixer.Sound("waves/ha.wav")
wrak_sound = pygame.mixer.Sound("waves/fra.wav")
# input to hold the username during runtime.
username = "@"+input("Enter the TikTok username followed with : ")
# Create Client instance.
client = TikTokLiveClient(unique_id=username)

# Create Queue to Handle requests 
request_queue = queue.Queue()

# Global variable to end the app
appisruning = True

# Destroy the window form event
def close_window(window):
    window.destroy()

# Show targeted message in a windows form using tkinter
def showMessage(usrnm, Comment, usrimg, soundid):
    root = tk.Tk()
    root.iconbitmap(default="myIcon.ico")
    root.overrideredirect(1)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0)
    if usrimg:
        # Load the image from the binary data
        with Image.open(io.BytesIO(usrimg)) as img:
            img_width, img_height = img.size
            # Adjust the window size based on the image size
            window_width = max(img_width, 300)
            window_height = max(img_height + 50, 150)
            # Create PhotoImage object from the image
            photo_img = ImageTk.PhotoImage(img)
    else:
        # Set default window size if no image is provided
        window_width = 300
        window_height = 150
        photo_img = None

    # get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # set window position to center of screen
    x = (screen_width // 2) - 150
    y = (screen_height // 2) - 75

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    popup_window = tk.Toplevel(root)
    popup_window.transient(root)
    popup_window.title(usrnm)
    popup_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    if photo_img:
        # create label with image
        image_label = tk.Label(popup_window, image=photo_img)
        image_label.pack()

    # create label with text
    text_label = tk.Label(popup_window, text=Comment)
    text_label.pack()

    root.update()
    # form time out based on milliseconds
    timegone = 4000

    # handle the soundid based on the message recived.
    # you can change the logic as you want..
    if soundid == 1:
        pygame.mixer.Sound.play(sambosa_sound)
    if soundid == 2:
        pygame.mixer.Sound.play(n3na3_sound)
    if soundid == 3:
        timegone = 6000
        pygame.mixer.Sound.play(kabso_sound)
    if soundid == 4:
        timegone = 10000
        pygame.mixer.Sound.play(hadeda_sound)
    if soundid == 5:
        timegone = 17000
        pygame.mixer.Sound.play(wrak_sound)
    # Schedule the window to timegone value
    popup_window.after(timegone, popup_window.destroy)

    # Wait for the popup_window to close before destroying the root window
    root.wait_window(popup_window)
    root.destroy()

def SayUser(usrnm):
    print(f"{usrnm} -> Joined")

def process_requests():
    while True:
        request = request_queue.get()
        if request is None:
            break
        if appisruning == False:
            break
        event_type = request[0]
        if event_type == 'comment':
            showMessage(*request[1:])
        elif event_type == 'gift':
            showMessage(*request[1:])
        elif event_type == 'like':
            unique_id, total_likes = request[1:]
            print(f"{unique_id} -> sent Likes -> {total_likes}")
        elif event_type == 'joined':
            nickname = request[1]
            SayUser(nickname)

        request_queue.task_done()


# Run Tiktok Client
def init_tiktok():
    client.run()

# Events Section, on_connect, on_comment, on_Gift, on_like, on_Joined
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)

async def on_comment(acommentevent: CommentEvent):
    if acommentevent.comment:
        usercm = acommentevent.comment
    else:
        usercm = ""
    usercm = usercm.strip()
    if usercm.isdigit():
        sentnum = int(usercm)
        if sentnum >= 1 and sentnum <=5:
            image_data: bytes = await acommentevent.user.avatar.download()
            request_queue.put(('comment', acommentevent.user.nickname, usercm, image_data, sentnum))

async def on_Gift(agiftevent: GiftEvent):
    if agiftevent.user.unique_id:
        print(agiftevent.gift.info.name)
        gift_name = agiftevent.user.unique_id
        gift_image_data = await agiftevent.gift.info.image.download()
        request_queue.put(('gift', agiftevent.user.nickname, gift_name, gift_image_data, 2))

async def on_like(alikeevent: LikeEvent):
    if alikeevent.user.unique_id:
        request_queue.put(('like', alikeevent.user.unique_id, alikeevent.total_likes))

async def on_Joined(Joinevent: LiveEvent):
    if Joinevent.user.unique_id:
        usrIdJoin = Joinevent.user.unique_id
        request_queue.put(('joined', usrIdJoin))

# End Of events Section

# close and stop handling of queue requests.
def cleanup():
    global appisruning 
    appisruning = False
    request_queue.put(None)
    processing_thread.join()
    client.close()
    client.loop.close()

# add listeners to the available events.
client.add_listener("comment", on_comment)
client.add_listener("gift", on_Gift)
client.add_listener("like", on_like)
client.add_listener("join", on_Joined)


# run the app.
if __name__ == '__main__':
    try:
        # Create a Thread To handle the requests queue.
        processing_thread = threading.Thread(target=process_requests)
        # start the thread
        processing_thread.start()
        # run tiktok Client.
        init_tiktok()
    except KeyboardInterrupt:
        print("Shutting down...")
        cleanup()
