# Parla Italiano Bot - Technical Details

## Technologies Used

### Current Stack
- **Python 3.x**: Primary programming language
- **aiogram**: Telegram bot framework
- **asyncpg**: Asynchronous PostgreSQL driver
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **asyncio**: Asynchronous programming

### Planned Stack
- **Python 3.x**: Primary programming language
- **aiogram**: Telegram bot framework
- **PostgreSQL**: Primary database for persistent storage
- **Docker**: Containerization for deployment
- **psycopg2**: PostgreSQL adapter for Python
- **python-dotenv**: Environment variable management
- **asyncpg**: Asynchronous PostgreSQL driver
- **pytest**: Testing framework
- **pydantic**: Data validation and serialization
- **openai**: LLM integration for content generation

## Development Setup

### Current Setup
- Modular Python package structure (partial)
- Docker container for consistent deployment
- PostgreSQL database container (via docker-compose)
- Environment variables for bot token and database
- Automated testing with pytest
- Migration system for database schema management

### Planned Setup
- Modular Python package structure
- Docker container for consistent deployment
- PostgreSQL database container (via docker-compose)
- Configuration management via config.ini
- Automated testing with pytest
- CI/CD pipeline for deployment

## Technical Constraints

### Current Constraints
- In-memory state management (lost on restart)
- Database-driven content (static updates via migrations)
- No user authentication
- Limited error handling
- Logging system implemented

### Planned Constraints
- PostgreSQL database schema design
- Docker container resource limits
- LLM API rate limits and costs
- Telegram API rate limits
- User authentication token security
- Configuration file security

## Dependencies

### Current Dependencies
```
aiogram
python-dotenv
asyncpg
pytest
pytest-asyncio
```

### Planned Dependencies
```
aiogram
psycopg2-binary
asyncpg
python-dotenv
pydantic
pytest
pytest-asyncio
openai
docker
```

## Tool Usage Patterns

### Current Patterns
- Direct function calls for game logic
- Simple dictionary for state management
- Inline keyboard for UI
- Basic callback handling
- Async database operations with connection pooling
- Migration-based database schema management
- File-based logging with structured output

### Planned Patterns
- Repository pattern for database access
- Service layer for business logic
- Middleware for authentication
- Event-driven architecture
- Configuration-driven behavior
- Logging for debugging and monitoring