# Parla Italiano Bot - Architecture

## Source Code Structure

### Current Structure
```
parla_italiano_bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot implementation
│   ├── database.py         # Database operations
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_game_logic.py
├── migrations/
│   └── 001_initial.sql     # Database schema and initial data
├── deploy.sh               # Deployment script
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker image definition
├── parla_italiano_bot.jpg  # Project image
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── run_migrations.sh       # Database migration runner
├── .gitignore              # Git ignore rules
└── .kilocode/              # Memory bank and rules
```

### Planned Structure
```
parla_italiano_bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot implementation
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
│   ├── models.py           # Data models
│   ├── game_logic.py       # Game logic implementation
│   ├── auth.py             # User authentication
│   ├── content_manager.py  # Content management
│   └── llm_service.py      # LLM integration
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_game_logic.py
│   └── test_database.py
├── config/
│   ├── config.ini          # Main configuration
│   └── docker-compose.yml  # Docker configuration
├── scripts/
│   ├── deploy.sh           # Deployment script
│   └── update.sh           # Update script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## Key Technical Decisions

### Current Implementation
- Using aiogram framework for Telegram bot functionality
- In-memory game state management with dictionary
- PostgreSQL database for persistent data storage
- Database-driven content with migration system
- Docker containerization for deployment
- Logging system with file output to /logs directory
- Automated migration execution
- Modular Python package structure (partial)
- Testing framework with pytest

### Planned Implementation
- PostgreSQL for persistent data storage
- User authentication system with token-based access
- Docker containerization for deployment
- Configuration management via config.ini
- LLM integration for dynamic content generation
- Modular architecture with clear separation of concerns

## Component Relationships

### Current Components
1. **Bot Handler**: Processes Telegram messages and callbacks (src/bot.py)
2. **Game Logic**: Manages game state and word ordering (in-memory in src/bot.py)
3. **Data Storage**: PostgreSQL database with tables for sentences and phrases
4. **Database Layer**: Handles PostgreSQL operations (src/database.py)

### Planned Components
1. **Bot Handler**: Processes Telegram messages and callbacks
2. **Game Logic**: Manages game state and word ordering
3. **User Auth**: Handles user authentication and authorization
4. **Content Manager**: Manages sentences and stories
5. **Config Manager**: Loads and manages configuration
6. **LLM Service**: Integrates with language models for content generation