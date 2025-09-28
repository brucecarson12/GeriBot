# GeriBot - Modular Structure

This directory contains the modularized GeriBot codebase, organized for better maintainability and scalability.

## Directory Structure

```
bot/
├── __init__.py                 # Bot package initialization
├── config.py                   # Configuration settings
├── models/                     # Data models
│   ├── __init__.py
│   └── participant.py         # Participant model for tournaments
├── services/                   # External service integrations
│   ├── __init__.py
│   ├── chess_com_service.py   # Chess.com API integration
│   ├── lichess_service.py     # Lichess API integration
│   ├── database_service.py    # Google Sheets database integration
│   └── puzzle_service.py      # Puzzle generation service
└── commands/                   # Command modules (Discord cogs)
    ├── __init__.py
    ├── general_commands.py    # General utility commands
    ├── chess_commands.py      # Chess.com related commands
    └── lichess_commands.py    # Lichess related commands
```

## Key Improvements

### 1. **Separation of Concerns**
- **Models**: Data structures and business logic
- **Services**: External API integrations and data processing
- **Commands**: Discord bot command handlers
- **Config**: Centralized configuration management

### 2. **Service Layer Architecture**
- **ChessComService**: Handles all Chess.com API interactions
- **LichessService**: Manages Lichess API calls
- **DatabaseService**: Google Sheets integration
- **PuzzleService**: Chess puzzle generation

### 3. **Command Organization**
- **GeneralCommands**: Basic bot functionality (hello, help, resources)
- **ChessCommands**: Chess.com specific features
- **LichessCommands**: Lichess specific features

### 4. **Error Handling**
- Proper exception handling in all services
- User-friendly error messages
- Graceful degradation when services fail

### 5. **Type Hints**
- Full type annotations for better code maintainability
- IDE support and static analysis

## Usage

The new modular structure is used in `main_new.py`:

```python
from bot.commands.general_commands import GeneralCommands
from bot.commands.chess_commands import ChessCommands
from bot.commands.lichess_commands import LichessCommands
```

## Benefits

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Services can be easily mocked and tested
3. **Scalability**: New features can be added as separate modules
4. **Reusability**: Services can be used across different command modules
5. **Configuration**: Centralized settings management
6. **Error Handling**: Consistent error management across all modules

## Migration

To migrate from the old monolithic structure:

1. Replace `main.py` with `main_new.py`
2. Update imports in any custom code
3. Move tournament logic to a separate service module
4. Implement proper state management for tournament variables

## Future Enhancements

- Tournament service module
- Caching service for API responses
- Logging service for better debugging
- Configuration validation
- Database connection pooling
