# Parla Italiano Bot - Architecture

## Source Code Structure

### Current Structure
```
parla_italiano_bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Entry point
│   ├── config.py           # Configuration management
│   ├── database/           # Modular database operations
│   │   ├── __init__.py
│   │   ├── connection.py   # Database connections and migrations
│   │   ├── users.py        # User profile management
│   │   ├── base.py         # Shared utilities and LLM integration
│   │   └── sentences.py    # Sentence feature operations
│   ├── bot_commands/       # Telegram command handlers
│   │   ├── __init__.py
│   │   ├── start.py        # /start command handler
│   │   ├── echo.py         # Echo message responses
│   │   ├── stats.py        # /stats command handler
│   │   ├── help.py         # /help command handler
│   │   └── rus.py          # /rus command handler (Russian translations)
│   ├── exercises/          # Learning exercise implementations
│   │   ├── __init__.py
│   │   └── sentence_ordering.py  # Sentence word ordering exercise
│   ├── state/             # User state management
│   │   ├── __init__.py
│   │   └── learning_state.py     # User learning state management
│   └── application/       # Application orchestration
│       ├── __init__.py
│       └── bot_app.py     # Main application orchestrator
├── tests/
│   ├── __init__.py
│   ├── test_bot.py        # Tests for bot commands and exercise logic
│   ├── test_learning_state.py  # Tests for learning state management
│   ├── test_database.py   # Tests for database operations
│   ├── test_config.py     # Tests for configuration management
│   ├── test_help_command.py  # Tests for /help command
│   ├── test_stats_command.py  # Tests for /stats command
│   └── test_rus_command.py  # Tests for /rus command (Russian translations)
├── migrations/
│   ├── 001_initial.sql    # Initial database schema
│   ├── 002_users.sql      # Users table
│   ├── 003_results_table.sql  # Results tracking
│   └── 004_russian_translation.sql  # Russian translations column
├── config.ini             # Configuration parameters
├── deploy.sh              # Deployment script
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker image definition
├── parla_italiano_bot.jpg # Project image
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── run_migrations.sh      # Database migration runner
├── .gitignore             # Git ignore rules
└── .kilocode/             # Memory bank and rules
```

## Key Technical Decisions

### Current Implementation
- Using aiogram framework for Telegram bot functionality
- Class-based learning state management with LearningState
- PostgreSQL database for persistent data storage
- Database-driven content with migration system
- Docker containerization for deployment
- Logging system with file output to /logs directory
- Automated migration execution
- Modular Python package structure (complete)
- Testing framework with pytest and pytest-asyncio
- Centralized configuration management with pydantic models
- LLM integration for dynamic content generation
- Separation of sensitive (env) and non-sensitive (config.ini) configuration
- Dependency injection for modularity and testability
- Clear separation of concerns with dedicated modules
- Russian translation feature with LLM integration for content generation
- Structured output models for Italian-Russian sentence pairs
- Configuration-driven validation for multiple languages

### Planned Implementation
- User authentication system with token-based access

## Component Relationships

### Current Components
1. **Configuration Manager**: Centralized configuration loading and validation (src/config.py)
2. **Application Orchestrator**: Main application class with dependency injection (src/application/bot_app.py)
3. **Learning State Manager**: User learning state management (src/state/learning_state.py)
4. **Exercise Modules**: Learning exercise implementations (src/exercises/)
   - **Sentence Ordering**: Word ordering exercise logic (src/exercises/sentence_ordering.py)
5. **Command Handlers**: Telegram bot command processing (src/bot_commands/)
   - **Start Handler**: /start command processing (src/bot_commands/start.py)
   - **Echo Handler**: Generic message responses (src/bot_commands/echo.py)
   - **Stats Handler**: /stats command processing (src/bot_commands/stats.py)
   - **Help Handler**: /help command processing (src/bot_commands/help.py)
   - **Rus Handler**: /rus command processing for Russian translations (src/bot_commands/rus.py)
6. **Data Storage**: PostgreSQL database with tables for sentences, phrases, users, and results
7. **Database Layer**: Modular database operations with separate repositories
   - **Connection Module**: Database connections, migrations, table counts, statistics (src/database/connection.py)
   - **User Module**: User profile management operations (src/database/users.py)
   - **Base Module**: Shared utilities, validation, LLM integration (src/database/base.py)
   - **Sentences Module**: Sentence feature operations with Russian translations (src/database/sentences.py)
8. **User Tracking**: Manages user profiles and access timestamps via get_or_create_user (src/database/users.py)
9. **Entry Point**: Simple application entry point (src/bot.py)
10. **Config Manager**: Loads and manages configuration with multi-language support

### Planned Components
1. **User Auth**: Handles user authentication and authorization
2. **Content Manager**: Manages sentences and stories
3. **Additional Exercise Modules**: Expandable system for new learning activities