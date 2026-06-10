# Ethics Navigator

A private chatbot for your own documents. You add your files, ask questions, and
get answers based on those files — **everything runs on your own computer and
nothing is ever sent to the internet.**

This guide is written for non-technical users. You only need to copy and paste a
couple of commands. Take it one step at a time.

---

## Step 1 — Install Docker Desktop

Docker is a free program that runs this app for you so you don't have to install
anything else. Think of it as a container that holds everything the app needs.

1. Go to **https://www.docker.com/products/docker-desktop/** and download Docker
   Desktop for your computer (Windows or Mac).
2. Install it like any other program, then **open it**.
3. Wait until it says it's running (you'll see a little **whale icon** 🐳 in your
   menu bar or system tray). Leave it running.

## Step 2 — Get the app onto your computer

If you were sent a link to this project on GitHub:

- Click the green **"Code"** button, then **"Download ZIP"**.
- Unzip the downloaded file. You'll get a folder called `ethics-navigator-tool`.

(If you know how to use Git, you can instead run `git clone <repo-url>`.)

## Step 3 — Start the app

1. Open a **terminal** (on Windows: "PowerShell"; on Mac: "Terminal").
2. Navigate into the folder you just unzipped. The easiest way: type `cd ` (with a
   space), then drag the `ethics-navigator-tool` folder onto the terminal window
   and press **Enter**.
3. Copy and paste this command, then press **Enter**:

   ```bash
   docker compose up --build
   ```

**The first time is slow** — it downloads the AI model (a few gigabytes), which
happens only once. You'll know it's ready when you see a line like:

```
app  |   You can now view your Streamlit app in your browser.
```

## Step 4 — Use it

1. Open your web browser and go to **http://localhost:8501**.
2. In the sidebar on the left, click **"Add documents"** and choose your files
   (PDF, TXT, or Markdown), then click **"Add to knowledge base"**. Wait for the
   green success message.
3. Type a question in the box at the bottom and press Enter. The answer will be
   based on your documents, and you can expand **"Sources"** to see which parts it
   used.

## Stopping and restarting

- To **stop** the app: go back to the terminal and press **Ctrl + C**, then run
  `docker compose down`.
- To **start it again later**: run `docker compose up` (no `--build` needed, and it
  won't re-download the model). Your documents are still there.

## Troubleshooting

- **Nothing loads at http://localhost:8501** — Make sure Docker Desktop is open and
  running (the whale icon). Give the app a minute to finish starting.
- **The first answer is slow** — The model is still warming up the first time.
  Later answers are faster.
- **I want to start completely fresh** — Run `docker compose down -v`. This clears
  the downloaded model and all indexed documents.

## Your privacy

Your documents and your questions never leave your computer. The AI model runs
locally inside Docker. Nothing is uploaded to any external service.
