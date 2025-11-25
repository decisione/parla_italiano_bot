# Parla Italiano Bot

A Telegram bot designed to help users learn Italian through interactive word ordering exercises.

## Features

- **Word Ordering Game**: Reorder scrambled Italian sentences to form correct phrases
- **Immediate Feedback**: Get instant feedback on your answers with encouraging messages
- **Interactive Interface**: Simple and intuitive interface with inline keyboard buttons
- **Progressive Learning**: Continuously practice with new sentences

## Installation

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- (Future) PostgreSQL database
- (Future) Docker

### Setup the development environment

1. Clone the repository:
```bash
git clone https://github.com/decisione/parla_italiano_bot.git
cd parla_italiano_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

5. Run the bot:
```bash
python parla_italiano_bot.py
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send the `/start` command to begin the word ordering game
3. Select words in the correct order to form Italian sentences
4. Receive feedback on your answers and continue with new sentences

## Project Structure

```
parla_italiano_bot/
├── parla_italiano_bot.py    # Main bot implementation
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── .env                    # Environment variables (not committed)
```

## Future Development

The project is planned to evolve with the following features:

### Phase 1: Infrastructure
- Docker containerization
- Deployment automation

### Phase 2: Configuration
- Configuration management system

### Phase 3: Database
- PostgreSQL database integration
- Database migration for existing data

### Phase 4: Authentication
- User authentication system

### Phase 5: Replenishment
- LLM integration for dynamic content generation

### Phase 6: Stories
- Stories mode implementation

## License

All rights reserved.
