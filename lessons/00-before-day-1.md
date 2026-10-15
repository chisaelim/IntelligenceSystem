# Before Day 1: get your computer ready

**Do this at home, before the first lesson.** The environment is a big download (about 3 to 5 GB), and it can take an hour or more on a slow connection. If you do it in class, you lose lesson time.

## What you need

| Item | Details |
|---|---|
| A computer | Windows 10 or 11, macOS, or Linux. 8 GB of memory is enough. |
| Free disk space | At least **15 GB** |
| A webcam | The built-in one is fine. If you have none, you will use a video file (ask your instructor). |
| Internet | For the downloads, and for Telegram on Days 10-15 |
| A Telegram account | On your phone (and optionally on the computer). It is free. |

## Step 1: Install Anaconda

Download **Anaconda Distribution** (free for learning) from `anaconda.com/download` and install it with the default options. (Miniconda or Miniforge also work.)

- **Windows:** after installing, open **Anaconda Prompt** from the Start menu. Use it for every command in this course.
- **macOS / Linux:** open a normal terminal. Type `conda --version`. If you see `command not found`, close the terminal and open a new one. If it still fails, ask your instructor.

## Step 2: Create the course environment

An *environment* is a separate toolbox with its own Python and packages. Yours is called `python-course`. Your instructor gives you the course folder. Open a terminal **inside that folder** and run the command for your system:

```bash
conda env create -f environment-windows.yml    # Windows
conda env create -f environment-macos.yml      # macOS with an Apple chip (M1, M2, M3...)
conda env create -f environment-linux.yml      # Linux
```

This downloads a lot. Leave the terminal open until it finishes. When it is done, check it:

```bash
conda activate python-course
python -c "import cv2, torch, ultralytics, requests, pandas; print('OK')"
```

You should see `OK`. (The first time, `ultralytics` may also print a line about creating settings: that is normal.)

| Problem | What to do |
|---|---|
| `CondaToSNonInteractiveError` | conda wants you to accept its terms of service. Run the `conda tos accept ...` command that the message prints, then try again. |
| An error about a **long path** (Windows) | Turn on Windows long paths (`LongPathsEnabled=1`, ask your instructor), then run the command again. |
| **Intel Mac** | The macOS file is for Apple chips. On an Intel Mac, open `environment-macos.yml`, delete the line that starts with `- tensorflow`, and run the command again. Everything else installs as written, and TensorFlow is not used in this course. |
| The download stops or is very slow | Run the same command again: it continues. Try another network if you can. |
| `EnvironmentNameConflict` / the environment exists | It is already installed. Use `conda env update -f environment-<your system>.yml --prune` to update it. |

## Step 3: Install VS Code

Download **Visual Studio Code** (free) from `code.visualstudio.com`. In the Extensions panel, install the **Python** extension (by Microsoft). You will set it up on Day 1.

## Step 4: Install Git

Check with `git --version`. If the command is not found:

| System | How |
|---|---|
| Windows | install **Git for Windows** from `git-scm.com` with the default options |
| macOS | run `xcode-select --install` |
| Linux | `sudo apt install git` (Ubuntu/Debian) |

## Step 5: Telegram and your camera

1. Install **Telegram** on your phone and create an account.
2. Test your webcam with any app (the camera app of your computer). Make sure no other program (Zoom, Teams) is using it.
3. **macOS:** the first time a program uses the camera, macOS will ask for permission. Say yes. **Windows:** check Settings > Privacy & security > Camera.

## Checklist

- [ ] `conda activate python-course` works.
- [ ] The `import` test prints `OK`.
- [ ] VS Code and the Python extension are installed.
- [ ] `git --version` works.
- [ ] You have a Telegram account.
- [ ] Your webcam works (or you know that you will use a video file).

If one of these fails, tell your instructor **before** Day 1.
