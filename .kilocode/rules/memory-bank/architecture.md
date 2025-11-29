# Parla Italiano Bot - Architecture

## Source Code Structure

### Current Structure
```
parla_italiano_bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot implementation
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_game_logic.py
│   ├── test_database.py
├── migrations/
│   └── 001_initial.sql     # Database schema and initial data
├── config.ini              # Configuration parameters
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
- Centralized configuration management with pydantic models
- Separation of sensitive (env) and non-sensitive (config.ini) configuration

### Planned Implementation
- PostgreSQL for persistent data storage
- User authentication system with token-based access
- Docker containerization for deployment
- Configuration management via config.ini
- LLM integration for dynamic content generation
- Modular architecture with clear separation of concerns

## Component Relationships

### Current Components
1. **Configuration Manager**: Centralized configuration loading and validation (src/config.py)
2. **Bot Handler**: Processes Telegram messages and callbacks (src/bot.py)
3. **Game Logic**: Manages game state and word ordering (in-memory in src/bot.py)
4. **Data Storage**: PostgreSQL database with tables for sentences, phrases, and users
5. **Database Layer**: Handles PostgreSQL operations (src/database.py)
6. **User Tracking**: Manages user profiles and access timestamps via get_or_create_user (src/database.py)

### Planned Components
1. **Bot Handler**: Processes Telegram messages and callbacks
2. **Game Logic**: Manages game state and word ordering
3. **User Auth**: Handles user authentication and authorization
4. **Content Manager**: Manages sentences and stories
5. **Config Manager**: Loads and manages configuration
6. **LLM Service**: Integrates with language models for content generation