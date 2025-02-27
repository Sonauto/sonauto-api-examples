
# 🎵 Sonauto API Examples

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Sonauto API](https://img.shields.io/badge/Sonauto-API-ff69b4.svg)](https://sonauto.ai)

> AI-powered music generation with just a few lines of code!

This repository contains example code for the [Sonauto AI Music Generation API](https://sonauto.ai), showcasing how to generate music, create transitions, and even produce singing telegram videos with simple Python scripts.

![Sonauto Music Banner](https://placekitten.com/1200/300)

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

## 🔑 API Keys

To use these examples, you'll need:

1. A Sonauto API key - [Get one here](https://sonauto.ai/developers)
2. For the singing telegram example, a Lemon Slice API key - [Register here](https://lemonslice.com)


## 🚀 Examples

### 1. Basic Song Generation

[`rock_song_generator.py`](examples/rock_song_generator.py) - Generate a complete rock song with just a few lines of code.

First, sub in your Sonauto API key.

Second, run it with:

```bash
python rock_song_generator.py
```

### 2. Song Transition Generator

[`transition_generator.py`](examples/transition_generator.py) - Create smooth transitions between any two songs downloaded from YouTube.

This script:
- Downloads two songs from YouTube URLs
- Generates a transition between them using Sonauto's API
- Exports a combined track with the transition

Don't forget to sub in your API key.

```bash
python examples/transition_generator.py --song1 "https://youtube.com/watch?v=dQw4w9WgXcQ" --song2 "https://youtube.com/watch?v=y6120QOlsfU" --transition-length 15
```

### 3. Singing Telegram Video Creator

[`singing_telegram.py`](examples/singing_telegram.py) - Create a personalized singing telegram video that combines Sonauto's music generation with Lemon Slice's AI video generation.

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