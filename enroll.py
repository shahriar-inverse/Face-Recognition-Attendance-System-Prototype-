import os
import pickle
import cv2
from insightface.app import FaceAnalysis

REFERENCE_DIR = "reference_photos"
OUTPUT_FILE = "enrolled_faces.pkl"
IMG_EXTS = (".jpg", ".jpeg", ".png")

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1, det_size=(640, 640))


def get_embedding(path):
    img = cv2.imread(path)
    if img is None:
        return None, "could not read file"
    faces = app.get(img)
    if len(faces) == 0:
        return None, "no face found"
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    return face.embedding, None


def sort_key(name):
    # numeric IDs sort as numbers (1,2,...,10,11) instead of text (1,10,11,2,...)
    try:
        return (0, int(name))
    except ValueError:
        return (1, name)


enrolled = {}

for entry in sorted(os.listdir(REFERENCE_DIR), key=lambda e: sort_key(os.path.splitext(e)[0])):
    full_path = os.path.join(REFERENCE_DIR, entry)

    if os.path.isdir(full_path):
        # a folder = one person, every image inside is one of their reference photos
        name = entry
        photo_paths = [os.path.join(full_path, f) for f in sorted(os.listdir(full_path))
                       if f.lower().endswith(IMG_EXTS)]
    elif entry.lower().endswith(IMG_EXTS):
        # a loose file = one person, one photo (old-style, still supported)
        name = os.path.splitext(entry)[0]
        photo_paths = [full_path]
    else:
        continue

    embeddings = []
    for photo_path in photo_paths:
        embedding, error = get_embedding(photo_path)
        if error:
            print(f"[SKIP] {photo_path}: {error}")
            continue
        embeddings.append(embedding)

    if embeddings:
        enrolled[name] = embeddings
        print(f"[OK] Enrolled: {name} ({len(embeddings)} photo(s))")
    else:
        print(f"[SKIP] {name}: no usable photos")

with open(OUTPUT_FILE, "wb") as f:
    pickle.dump(enrolled, f)

total_photos = sum(len(v) for v in enrolled.values())
print(f"\nDone. Enrolled {len(enrolled)} people from {total_photos} photo(s) -> {OUTPUT_FILE}")
