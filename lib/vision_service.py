import argparse
import os.path
import cv2
import time
import threading

import numpy as np

from lib import caption_generation, edge_tts_playback
from lib import image_processing
import config
from lib.response_generation import generate_response


# import whisper_cpp
enable_init_caption_generation=False

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
        # print("vision service start")
        if not self.started:
            if enable_init_caption_generation:
                caption_generation.init()
            self.main_loop()

    # convert frame to PIL image format and generate caption for a frame
    def process_frame(self, frame):
        start = time.time()
        pil_image = image_processing.convert_frame_to_pil_image(frame)
        caption = caption_generation.generate_caption(pil_image)
        # print(f"caption: {caption}")

        self.current_time = time.time()  # track current time for processing time comparison
        if self.current_time - self.last_generation_time >= 1:  # generate captions every 1 seconds
            if caption and caption not in self.previous_captions and caption not in self.sequence_list:
                self.sequence_list.append(('Caption', caption))  # add caption to sequence list
                # print(f"caption append: {caption}")
                self.previous_captions.append(caption)  # add caption to list of previous captions
                if len(self.previous_captions) > 10:  # limit list of captions to 10 items
                    self.previous_captions.pop(0)
            self.last_generation_time = self.current_time  # update last generation time

        use_time=time.time() - start;
        # print(f"process_frame: {use_time}")

    def display_frame1(self, frame):
        """
        Function to display a frame on the screen and overlay the previous captions on top of it.
        """
        with self.lock:  # synchronize with lock
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            thickness = 2
            color = (0, 255, 0)
            org = (10, 50)

            captions_str = "Caption"
            if len(self.sequence_list) > 0:
                captions_str = self.sequence_list[-1][1]
            # self.captions_str = self.captions_str
            flipped_frame = cv2.flip(frame, 1)  # Flip the frame horizontally
            cv2.putText(frame, captions_str, org, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.imshow('frame', flipped_frame)

    def save_frame(self, frame, image_path="captured_image.jpg"):
        """
        Save the given frame as an image file.
        
        Args:
            frame: The frame to be saved.
            image_path: The path where the image will be saved.
        """
        # Convert the frame to RGB (if needed)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the frame as an image file
        import time
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_path_with_time = f"captured/{image_path.split('.')[0]}_{timestamp}.{image_path.split('.')[-1]}"
        import os

        # Create the 'captured' directory if it doesn't exist
        if not os.path.exists('captured'):
            os.makedirs('captured')
        cv2.imwrite(image_path_with_time, frame_rgb)
        cv2.imwrite(image_path, frame_rgb)

    def display_frame(self, frame):
        """
        Function to display a frame on the screen and overlay the previous captions on top of it.
        """
        with self.lock:  # synchronize with lock
            font = cv2.FONT_HERSHEY_SIMPLEX
            color = (255, 255, 255)

            if len(self.sequence_list) > 0:
                if len(self.sequence_list) > 1:
                    # captions_str = self.sequence_list[-2][1] + '\n' + self.sequence_list[-1][
                    #     1]  # Get the last caption in the list
                    captions_str = self.sequence_list[-1][1]  # Get the last caption in the list
                else:
                    captions_str = self.sequence_list[-1][1]  # Get the last caption in the list
            else:
                captions_str = "No Captions"

            # Determine font size based on the height of the text
            font_scale = 0.5
            thickness = 1
            org = (10, 20)

            while True:
                (text_width, text_height), _ = cv2.getTextSize(captions_str, font, font_scale, thickness)
                if text_width <= frame.shape[1] - 20:  # Check if the text fits within the frame
                    break
                font_scale -= 0.1

            # Adjust text position to center it horizontally
            org = ((frame.shape[1] - text_width) // 2, org[1] + text_height)
            rotated_frame = cv2.flip(frame, 1)  # Flip the frame horizontally

            cv2.putText(rotated_frame, captions_str, org, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.imshow("frame", rotated_frame)

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
                    edge_tts_playback.playTTS(response.replace('Alpha-Co-Bot', ''), config.settings.edge_tts_voice)

    def main_loop(self):
        # print("start vision main_loop")
        # create VideoCapture object for camera feed
        if config.settings.car_camera_stream_enable and config.settings.car_camera_stream_url:
            self.cap = cv2.VideoCapture(config.settings.car_camera_stream_url)
        else:
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
                time.sleep(5)
                continue
                # break

            self.current_time = time.time()
            if self.current_time - self.last_process_time >= 20:  # process frame every 20 seconds
                self.save_frame(frame)
                if enable_init_caption_generation:
                    t = threading.Thread(target=self.process_frame, args=(frame,))
                    t.start()
                self.last_process_time = self.current_time
            
            self.display_frame(frame)

            if cv2.waitKey(1) == ord('q') or (cv2.waitKey(1) & 0xFF == 27):
                break

        self.cap.release()
        cv2.destroyAllWindows()


vision = VisionService()


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
