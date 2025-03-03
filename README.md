
# 🎵 Sonauto API Examples

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Sonauto API](https://img.shields.io/badge/Sonauto-API-ff69b4.svg)](https://sonauto.ai)

> AI-powered music generation with just a few lines of code!

This repository contains example code for the [Sonauto AI Music Generation API](https://sonauto.ai), showcasing how to generate music, create transitions, and even produce singing telegram videos with simple Python scripts.

## 📋 Table of Contents

- [Installation](#installation)
- [API Keys](#api-keys)
- [Examples](#examples)
  - [1. Basic Song Generation](#1-basic-song-generation)
  - [2. Song Transition Generator](#2-song-transition-generator)
  - [3. Singing Telegram Video Creator](#3-singing-telegram-video-creator)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/sonauto/sonauto-api-examples.git
cd api-examples
pip install -r requirements.txt
```

Alternatively, install the dependencies with poetry or uv.

## 🔑 API Keys

To use these examples, you'll need:

1. A Sonauto API key - [Get one here](https://sonauto.ai/developers)
2. For the singing telegram example, a Lemon Slice API key - [Register here](https://lemonslice.com)


## 🚀 Examples

### 1. Basic Song Generation

[`rock_song_generator.py`](rock_song_generator.py) - Generate a complete rock song with just a few lines of code.

First, sub in your Sonauto API key.

Second, run it with:

```bash
python rock_song_generator.py
```

### 2. Song Transition Generator

[`transition_generator.py`](transition_generator.py) - Create smooth transitions between any two songs downloaded from YouTube.

This script:
- Downloads two songs from YouTube video IDs
- Generates a transition between them using Sonauto's API
- Exports a combined track with the transition

Don't forget to sub in your API key.

Example: Smash Mouth to Rick Astley
```bash
python song_transition.py ec1LhrCmzwI dQw4w9WgXcQ --trim-to-start 13 --trim-from-end 0.5 --silence 20
```

#### Parameters

- **URL1/URL2**: YouTube URLs or video IDs (required)
- **--song-duration**: Duration in seconds to use from each song (default: 45)
- **--silence**: Duration of silence between songs in seconds (default: 5)
- **--trim-from-end**: Seconds to trim from the end of the first song (default: 0)
- **--trim-to-start**: Seconds to trim from the beginning of the second song (default: 0)
- **--output**: Custom filename for the final transition (default: transition_[TASK_ID].ogg)
- **--pre-inpaint-output**: Filename for the pre-inpainting version (default: pre_inpaint_[TIMESTAMP].mp3)


### 3. Singing Telegram Video Creator

[`singing_telegram.py`](singing_telegram.py) - Create a personalized singing telegram video that combines Sonauto's music generation with Lemon Slice's AI video generation.

This example:
- Generates custom lyrics about the recipient based on your input
- Creates a personalized song in the style of your choice
- Uses Lemon Slice API to generate a video of a character singing your custom song
- Combines everything into a ready-to-share singing telegram video

Don't forget to grab a [Lemon Slice API key](https://lemonslice.com/developer) and set your .env file.

```bash
python singing_telegram.py --recipient "Sarah" --occasion "birthday" --message "she is turning 30 and loves hiking" --style "pop"
```

## 📚 Documentation

- [Sonauto API Documentation](https://sonauto.ai/developers)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ by the Sonauto Team</p>

<p align="center">
  <a href="https://x.com/SonautoAI">Twitter</a> •
  <a href="https://discord.gg/pfXar3ChH8">Discord</a> •
  <a href="https://sonauto.ai">Website</a>
</p>