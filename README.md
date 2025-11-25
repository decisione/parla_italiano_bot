# Parla Italiano Bot

A Telegram bot designed to help users learn Italian through interactive word ordering exercises.

## Features

- **Word Ordering Game**: Reorder scrambled Italian sentences to form correct phrases
- **Immediate Feedback**: Get instant feedback on your answers with encouraging messages
- **Interactive Interface**: Simple and intuitive interface with inline keyboard buttons
- **Progressive Learning**: Continuously practice with new sentences

## Project Structure

```
parla_italiano_bot/
├── parla_italiano_bot.py    # Main bot implementation
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── .env                    # Environment variables (not committed)
```

## Installation

### Prerequisites

- Python 3.12 or higher
- Telegram Bot Token

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

### Run in the development environment

- Run the bot:
```bash
python parla_italiano_bot.py
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send the `/start` command to begin the word ordering game
3. Select words in the correct order to form Italian sentences
4. Receive feedback on your answers and continue with new sentences

## Deployment into production enviroment

### Prerequisites on target host

- Docker
- Docker Compose

### Deployment

1. Run the script on the development host:
```bash
./deploy.sh
```

2. Monitor logs if needed (on production host):
```bash
cd /opt/parla_italiano_bot && docker compose -f docker-compose.yml logs
```

3. Clean up old images (on production host):
```bash
docker image prune
```

## Testing

- Run tests using pytest:
```bash
pytest
```

## Future Development

The project is planned to evolve with the following features:

### Phase 3: Configuration
- Configuration management system using config.ini
- Folder and file structure refactoring

### Phase 4: Database
- PostgreSQL database for persistent storage
- Database migration for existing data

### Phase 5: Authorization
- User authorization system

### Phase 6: Replenishment
- LLM integration for dynamic content generation

### Phase 7: Stories
- Stories mode implementation

## License

All rights reserved.
