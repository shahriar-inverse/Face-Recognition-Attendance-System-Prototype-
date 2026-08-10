# Attendance System.

## Quick Start

1. Download the ZIP file from this repo
2. Extract it to a folder and go to that folder
    for example:
   `cd Face-Recognition-Attendance-System-Prototype--main`
3. Prepare your reference photos (.jpg)


## Installation

### Linux / Mac

```
bash setup.sh
source venv/bin/activate
```

This creates a virtual environment and installs all dependencies. The face-recognition model (~280MB) downloads automatically on first use.
(Native Windows Python often fails compiling insightface - WSL2 is the easiest solution)

## Setting up your database

Create a `reference_photos` folder in the same directory as the Python files.

**Folder structure:**

Each person gets their own numbered folder with one or more photos:

```
reference_photos/
├── 1/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── 2/
│   ├── photo1.jpg
│   └── photo2.jpg
├── 3/
│   └── photo1.jpg
└── 4/
    ├── photo1.jpg
    ├── photo2.jpg
    └── photo3.jpg
```
![Database Structure](database-structure.jpeg)

**Rules:**
- Folder name = Student ID or ID and Name. (1, 2, 3, or 01 Simi, 02 Kaswser etc)
- Photos must be `.jpg` format
- Multiple photos per person = better accuracy (use different angles/lighting)
- At least one clear, front-facing photo per person recommended

## Usage

### Step 1: Enroll

```bash
python3 enroll.py
```

This extracts face embeddings from all reference photos and saves them to `enrolled_faces.pkl`.

**Output example:**
```
[OK] Enrolled: 1 (3 photo(s))
[OK] Enrolled: 2 (2 photo(s))
[SKIP] reference_photos/3/photo1.jpg: no face found
[OK] Enrolled: 4 (1 photo(s))

Done. Enrolled 3 people from 6 photo(s) -> enrolled_faces.pkl
```

If anyone is skipped, replace that photo with a clearer one and re-run.

### Step 2: Take Attendance

Place your group photo in the same folder as the scripts and name it `group_photo.jpg`.

```
python3 attendance.py
```

**Output files:**

1. **`attendance.csv`** - the attendance list
   ```
   Name,Status
   1,Present
   2,Absent
   3,Present
   4,Present
   ```

2. **`group_photo_annotated.jpg`** - the group photo with face detections marked
   - **Green box + name** = matched (present)
   - **Red box + score** = no match (unknown)

**Always check the annotated photo first** to verify detections are correct before trusting the CSV.

## Improving accuracy

If matches are wrong or people are missed, adjust the threshold in `attendance.py`:

```python
THRESHOLD = 0.45
```

- **Raise to 0.50-0.55** if you're getting false matches
- **Lower to 0.35-0.40** if real people aren't being matched

Then re-run `python3 attendance.py`.

## How it works (Technical)

- **Detection:** RetinaFace algorithm (finds faces in images)
- **Recognition:** ArcFace embeddings (512-dimensional face vectors, compared via cosine similarity)
- **Matching:** Each detected face is compared against all enrolled reference photos; best match above threshold = present
- **Hardware:** CPU-only (no GPU required)
- **Speed:** ~0.3-1 second per group photo on standard hardware

## Updating the database

**Add a new person:**
- Create folder `reference_photos/5/` with their photos
- Run `python3 enroll.py`
- Run `python3 attendance.py`

**Replace someone's photos:**
- Replace files in their folder
- Run `python3 enroll.py`

**Remove someone:**
- Delete their folder
- Run `python3 enroll.py`

## Troubleshooting

**Setup failed / packages won't install**
- Make sure you ran `bash setup.sh` and `source venv/bin/activate`

**"No face found" errors during enrollment**
- Photos are blurry, too small, or taken at bad angles
- Replace with clearer, front-facing photos and re-run `enroll.py`

**Many people marked "Unknown" in attendance**
- Group photo resolution too low (faces too small to recognize)
- Lighting in group photo very different from reference photos
- THRESHOLD set too high (lower it)
- People's appearance changed (different hairstyle, glasses, makeup)

**Face detected but wrong name matched**
- Increase THRESHOLD (e.g., 0.50 or 0.55)
- Add more/better reference photos for that person
- Re-run `enroll.py` then `attendance.py`

## Privacy

This repo contains code only - no face data or photos. All your `reference_photos`, `enrolled_faces.pkl`, group photos, and attendance results stay on your machine only.
