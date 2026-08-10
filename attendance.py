import pickle
import csv
import cv2
import numpy as np
from insightface.app import FaceAnalysis

ENROLLED_FILE = "enrolled_faces.pkl"
GROUP_PHOTO = "group_photo.jpg"
OUTPUT_CSV = "attendance.csv"
ANNOTATED_OUTPUT = "group_photo_annotated.jpg"
THRESHOLD = 0.45  # raise if wrong matches happen, lower if real matches are missed

with open(ENROLLED_FILE, "rb") as f:
    enrolled = pickle.load(f)  # {name: [embedding, embedding, ...]}

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1, det_size=(640, 640))

img = cv2.imread(GROUP_PHOTO)
if img is None:
    raise SystemExit(f"Could not read {GROUP_PHOTO}")

faces = app.get(img)
print(f"Detected {len(faces)} face(s) in the group photo")


def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def sort_key(name):
    # numeric IDs sort as numbers (1,2,...,10,11) instead of text (1,10,11,2,...)
    try:
        return (0, int(name))
    except ValueError:
        return (1, name)


present = set()
annotated = img.copy()

for face in faces:
    best_name, best_score = None, -1
    for name, ref_embeddings in enrolled.items():
        # a person matches if the detected face is close to ANY of their reference photos
        score = max(cosine_sim(face.embedding, ref) for ref in ref_embeddings)
        if score > best_score:
            best_name, best_score = name, score

    box = face.bbox.astype(int)
    if best_score >= THRESHOLD:
        present.add(best_name)
        label, color = f"{best_name} ({best_score:.2f})", (0, 255, 0)
    else:
        label, color = f"Unknown ({best_score:.2f})", (0, 0, 255)

    cv2.rectangle(annotated, (box[0], box[1]), (box[2], box[3]), color, 2)
    cv2.putText(annotated, label, (box[0], max(box[1] - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

cv2.imwrite(ANNOTATED_OUTPUT, annotated)

absent = sorted(set(enrolled.keys()) - present, key=sort_key)

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Status"])
    for name in sorted(enrolled.keys(), key=sort_key):
        writer.writerow([name, "Present" if name in present else "Absent"])

print(f"\nPresent: {len(present)} / {len(enrolled)}")
print(f"Absent: {', '.join(absent) if absent else 'None'}")
print(f"CSV saved -> {OUTPUT_CSV}")
print(f"Annotated photo saved -> {ANNOTATED_OUTPUT} (check this to catch mismatches)")
