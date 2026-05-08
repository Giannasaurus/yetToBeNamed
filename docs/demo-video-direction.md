# PhysiVision demo video direction

## Goal

Make the Canva demo feel like the app itself: a clear, modern physics tool with a calm scientific interface, not a generic startup pitch deck.

Use the existing app UI as the source of truth:

- Product name: PhysiVision
- Kicker: Video-based physics estimation
- Core promise: Estimate damping and spring constant from ordinary motion videos using computer vision and a damped harmonic oscillator model.
- UI tone: precise, classroom-friendly, technical but approachable

## Visual System For Canva

Use these Canva styles across all slides and video frames.

### Colors

- Background: `#FAF9F6`
- Text: `#28282B`
- Primary action purple: `#8B5CF6`
- Strong purple: `#6D28D9`
- Soft purple panel: `#F1EBFF`
- Orange accent: `#FF9B22`
- Strong orange: `#E57912`
- Blue accent: `#5F8FF5`
- Soft blue: `#E8F1FF`
- White surface: `#FFFFFF`

### Typography

- Use Inter everywhere.
- Titles: bold or extra bold, dark text or purple.
- Labels: uppercase, small, orange or strong purple.
- Body copy: short and direct. Avoid decorative script fonts or long paragraphs.

### Layout

- Use the app's off-white background with a subtle square grid.
- Use white surfaces and soft purple panels for content blocks.
- Keep panel corners rounded, but not pill-shaped.
- Use dashed purple borders for upload/process moments.
- Use orange and blue only as data accents, callouts, and chart lines.
- Avoid stock photos, heavy gradients, neon glows, and unrelated science clip art.

### Motion

- Keep motion clean: slide up, fade, simple line drawing, chart reveal, cursor zoom.
- Use quick UI zooms to guide attention.
- Avoid spin, bounce, confetti, or high-energy template transitions.

## Recommended Video Structure

Target length: 75 to 95 seconds.

### 1. Opening Problem, 0:00-0:08

Visual:
Show a clean app-style title screen on the off-white grid background. Add a small looping spring or pendulum clip in a white rounded panel.

On-screen copy:

```text
PhysiVision
Video-based physics estimation
```

Voiceover:

```text
Measuring spring behavior usually requires sensors, setup time, or manual data collection. PhysiVision estimates key physics values from an ordinary motion video.
```

### 2. Core Idea, 0:08-0:18

Visual:
Three app-style tags appear: Upload a video, Track motion, Fit the model.

On-screen copy:

```text
From motion video to physics parameters
```

Voiceover:

```text
The app tracks the object's position frame by frame, converts that motion into a time series, and fits it to a damped harmonic oscillator model.
```

### 3. Methodology, 0:18-0:42

Visual:
Use four horizontal steps, styled like UI cards. Each step should use one accent color sparingly.

Step 1:

```text
1. Detect the object
The first frame is used to isolate a trackable object.
```

Step 2:

```text
2. Track center position
Computer vision follows the object and records x/y center points over time.
```

Step 3:

```text
3. Clean the signal
The vertical motion is smoothed, centered, and detrended.
```

Step 4:

```text
4. Fit the physics model
The motion is matched to a damped oscillator to estimate damping, frequency, and spring constant.
```

Voiceover:

```text
First, PhysiVision isolates the moving object and tracks its center position across the video. Then it smooths and centers the displacement signal. From there, it estimates the dominant frequency, measures amplitude decay from motion peaks, and fits the observed motion to a damped oscillator.
```

Optional formula frame:

```text
y(t) = A e^(-gamma t) cos(omega t + phi)
k = m omega0^2
zeta = gamma / omega0
```

Keep this formula slide visual and brief. It should feel like a transparent method note, not a math lecture.

### 4. App Demo, Upload, 0:42-0:55

Visual:
Screen record the app at `http://127.0.0.1:5173/`.

Shot list:

- Show the header: PhysiVision, No sensors, OpenCV tracking, Damped motion fit.
- Drag or select a video.
- Show the uploaded video preview.
- Enter object mass and choose unit.
- Click Upload & Analyze.

On-screen copy:

```text
Upload any clear oscillation video
```

Voiceover:

```text
In the app, the user uploads a clear spring or pendulum video, enters the object's mass, and starts the analysis.
```

### 5. App Demo, Results, 0:55-1:15

Visual:
Show the result state. Zoom into the Spring Behavior summary first, then the results and charts.

Callouts:

```text
Damping ratio
Spring constant
Motion fit
Energy decay
Phase space
Amplitude decay
```

Voiceover:

```text
PhysiVision returns a plain-language behavior summary, the estimated spring constant and damping values, and visual checks for fit quality, energy change, phase space, and amplitude decay.
```

### 6. Why It Matters, 1:15-1:25

Visual:
Show three white cards on the app background.

On-screen copy:

```text
No extra sensors
Fast visual analysis
Physics you can inspect
```

Voiceover:

```text
The result is a lightweight way to turn motion videos into measurable physics, while still showing the data behind the estimate.
```

### 7. Close, 1:25-1:32

Visual:
Return to the app hero view or a polished final screenshot.

On-screen copy:

```text
PhysiVision
Estimate motion. Explain behavior.
```

Voiceover:

```text
PhysiVision makes motion analysis more accessible by combining computer vision with a physics model students can understand and inspect.
```

## Canva Redesign Checklist

- Replace template colors with the app palette above.
- Put the off-white grid background on every slide.
- Use Inter only.
- Replace generic icons with app-like UI blocks, chart lines, upload states, and simple step cards.
- Keep text short enough to read on mute.
- Use actual app screenshots or recordings for the demo section.
- Make every section look like it belongs beside the app, not like a separate brand campaign.

## Recording Checklist

- Use a 16:9 recording canvas.
- Record the browser at full width, ideally 1440 by 900 or larger.
- Hide bookmarks and unrelated browser UI if possible.
- Use `backend/actualspring.mp4` as the demo upload asset unless a cleaner video is available.
- Keep the cursor movement slow and intentional.
- After results load, pause on the summary long enough for viewers to understand it.

## Suggested Asset List

- App opening screenshot.
- Upload empty state screenshot.
- Uploaded video preview screenshot.
- Results summary screenshot.
- Charts screenshot.
- Short screen recording of the full upload and analyze flow.
- Optional cropped clip of the original spring video.
