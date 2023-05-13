import argparse
import os.path
import cv2
import time
import threading
from lib import caption_generation, edge_tts_playback
from lib import image_processing
import config
from lib.response_generation import generate_response


# import whisper_cpp

class VisionService:
    def __init__(self):
        # initialize variable for tracking processing times
        self.last_process_time = time.time()
        self.last_generation_time = time.time()
        self.previous_captions = []  # initialize variables for tracking previous captions and responses
        self.previous_responses = []
        self.lock = threading.Lock()  # initialize lock for threading synchronization
        self.sequence_list = []  # initialize list to hold generated captions, user input, and responses in sequence
        self.started = False

    def start(self):
        # self.main_loop()
        if not vision.started:
            caption_generation.init()
            threading.Thread(target=vision.main_loop()).start()  # start thread to wait for user input

    # convert frame to PIL image format and generate caption for a frame
    def process_frame(self, frame):
        pil_image = image_processing.convert_frame_to_pil_image(frame)
        caption = caption_generation.generate_caption(pil_image)
        # print(f"caption: {caption}")

        self.current_time = time.time()  # track current time for processing time comparison
        if self.current_time - self.last_generation_time >= 5:  # generate captions every 5 seconds
            if caption and caption not in self.previous_captions and caption not in self.sequence_list:
                self.sequence_list.append(('Caption', caption))  # add caption to sequence list
                print(f"caption append: {caption}")
                self.previous_captions.append(caption)  # add caption to list of previous captions
                if len(self.previous_captions) > 10:  # limit list of captions to 10 items
                    self.previous_captions.pop(0)
            self.last_generation_time = self.current_time  # update last generation time


    def display_frame(self, frame):
        """
        Function to display a frame on the screen and overlay the previous captions on top of it.
        """
        global previous_captions
        with self.lock:  # synchronize with lock
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.0
            thickness = 1
            color = (0, 0, 0)
            org = (10, 20)
            self.captions_str = '\n'.join(self.previous_captions)
            cv2.putText(frame, self.captions_str, org, font, font_scale, color, thickness, cv2.LINE_AA)
            flipped_frame = cv2.flip(frame, 1)  # Flip the frame horizontally
            cv2.imshow('frame', flipped_frame)

    def get_user_input(self):
        import sys
        # Set the console encoding to support Chinese input
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
        while True:
            sys.stdout.write("Ask: ")
            sys.stdout.flush()
            user_input = sys.stdin.readline().strip()
            # user_input = input('What do you say now? ')
            if user_input:
                # user_input = user_input.encode('utf-8').decode('unicode_escape')
                # user_input = user_input.encode('utf-8')
                self.sequence_list.append(('user_input', user_input))  # add user input to sequence list
                response = generate_response(sequence_list=self.sequence_list)
                # while response in previous_responses:  # ensure response is unique
                #     response = generate_response(' '.join(previous_captions), user_input)

                self.previous_responses.append(response)  # add response to list of previous responses
                self.sequence_list.append(('Alpha-Co-Bot', response))  # add response to sequence list
                if len(self.previous_responses) > 10:
                    self.previous_responses.pop(0)

                print(response)  # print response to console
                if config.settings.edge_tts_enable:
                    edge_tts_playback.playTTS(response.replace('Alpha-Co-Bot',''), config.settings.edge_tts_voice)


    def main_loop(self):
        # create VideoCapture object for camera feed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)

        self.started = True
        global last_process_time
        # threading.Thread(target=get_user_input).start()  # start thread to wait for user input
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error capturing frame, exiting.")
                break

            self.current_time = time.time()
            if self.current_time - self.last_process_time >= 5:  # process frame every 5 seconds
                t = threading.Thread(target=self.process_frame, args=(frame,))
                t.start()
                self.last_process_time = self.current_time

            self.display_frame(frame)

            if cv2.waitKey(1) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

vision = VisionService()
# if not vision.started:
#     threading.Thread(target=vision.main_loop()).start()  # start thread to wait for user input

def setup_config(config_file):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")

    settings = config.load_config(config_file)

    # print("OpenAI API Key:", settings.openai_api_key)
    print("Enable OpenAI:", settings.enable_openai)
    print("Enable enable_mps:", settings.enable_mps)
    print("openai_api_base_url:", settings.openai_api_base_url)
    print("blip_model:", settings.blip_model)
    print("whisper_cpp_path:", settings.whisper_cpp_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example with config file support.")
    parser.add_argument("--config", dest="config", default="config.json", help="Path to the config file")
    args = parser.parse_args()
    setup_config(args.config)
    caption_generation.init()

    # whisper_cpp.start_whispercpp()
    # main_loop()
