import os
import cv2
import numpy as np


def create_placeholder_video(filename, text, duration=5):
    """
    Create a simple placeholder video with text
    """
    # Create videos directory if it doesn't exist
    os.makedirs('static/videos', exist_ok=True)

    # Video settings
    frame_size = (640, 480)
    fps = 24
    total_frames = duration * fps

    # Create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f'static/videos/{filename}', fourcc, fps, frame_size)

    for i in range(total_frames):
        # Create a frame with gradient background
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Create gradient background
        for y in range(480):
            for x in range(640):
                frame[y, x] = [
                    (x + y) % 256,  # R
                    (x * 2) % 256,  # G
                    (y * 2) % 256  # B
                ]

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (640 - text_size[0]) // 2
        text_y = (480 + text_size[1]) // 2

        cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, f'Sample Video - Frame {i + 1}/{total_frames}',
                    (50, 50), font, 0.7, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"Created: static/videos/{filename}")


def main():
    """Create all sample videos"""
    videos_to_create = {
        'proposal.mp4': 'Romantic Proposal',
        'valentines.mp4': 'Valentine\'s Day',
        'anniversary.mp4': 'Anniversary Celebration',
        'birthday.mp4': 'Birthday Surprise'
    }

    for filename, text in videos_to_create.items():
        create_placeholder_video(filename, text)
        print(f"✓ Created {filename}")

    print("\nAll sample videos created successfully!")
    print("Location: static/videos/")


if __name__ == "__main__":
    main()