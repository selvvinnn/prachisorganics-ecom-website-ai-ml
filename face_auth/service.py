import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceAuthService:
    def __init__(self):
        print("Loading Face Recognition Model...")

        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(ctx_id=0, det_size=(640, 640))

        print("Face recognition model loaded successfully")

    def bytes_to_image(self, image_bytes):
        """
        Convert uploaded image bytes into OpenCV image.
        """
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img

    def calculate_brightness(self, img):
        """
        Calculate average brightness of image.
        Higher = brighter.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))

    def calculate_blur_score(self, img):
        """
        Calculate image sharpness using Laplacian variance.
        Higher = sharper.
        Lower = blurrier.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def get_face_embedding(self, image_bytes):
        """
        Detect face, run quality checks, and return embedding.
        """

        img = self.bytes_to_image(image_bytes)

        if img is None:
            return None, "Invalid image. Please try again."

        brightness = self.calculate_brightness(img)
        blur_score = self.calculate_blur_score(img)

        if brightness < 45:
            return None, "Image is too dark. Please move to better lighting."

        if blur_score < 35:
            return None, "Image is too blurry. Please keep your face steady."

        faces = self.app.get(img)

        if len(faces) == 0:
            return None, "No face detected. Please keep your face inside the camera."

        if len(faces) > 1:
            return None, "Multiple faces detected. Only one person should be in frame."

        face = faces[0]

        detection_score = float(face.det_score)

        if detection_score < 0.65:
            return None, "Face detection confidence is low. Please face the camera clearly."

        x1, y1, x2, y2 = face.bbox
        face_width = x2 - x1
        face_height = y2 - y1

        if face_width < 120 or face_height < 120:
            return None, "Face is too far from camera. Please move closer."

        embedding = face.embedding

        if embedding is None:
            return None, "Could not generate face embedding. Please try again."

        return embedding.tolist(), None

    def compare_embeddings(self, embedding1, embedding2):
        """
        Compare two embeddings using cosine similarity.
        Returns score between -1 and 1.
        Higher means more similar.
        """

        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)

        similarity = np.dot(emb1, emb2) / (
            np.linalg.norm(emb1) * np.linalg.norm(emb2)
        )

        return float(similarity)


face_service = FaceAuthService()