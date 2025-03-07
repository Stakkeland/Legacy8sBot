# Legacy8sBot

## Overview
Legacy8sBot is a Discord bot designed to manage game queues and facilitate 8s creations on legacy Call of Duty titles. It allows users to create accounts, join match queues, gain skill rating (SR), and become a competitive Call of Duty grandmaster.

## Project Structure
```
Legacy8sBot
├── __pycache__/
│   ├── commands.cpython-311.pyc
│   ├── database.cpython-311.pyc
│   ├── maps.cpython-311.pyc
│   ├── match_manager.cpython-311.pyc
│   ├── queue_manager.cpython-311.pyc
│   ├── voting.cpython-311.pyc
├── -- SQLite queries.sql
├── .gitignore
├── bot.py
├── commands.py
├── database.py
├── maps.py
├── match_manager.py
├── queue_manager.py
├── users.db
├── voting.py
```

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using the following command:
   ```sh
   pip install -r requirements.txt
   ```
4. Ensure you have a valid Discord bot token and update it in the `bot.py` file.

## Usage
- Run the bot by executing the `bot.py` file:
  ```sh
  python bot.py
  ```
- Use the following commands in Discord:
  - `!create_account <location>`: Create a new user account with the specified location.
  - `!change_location <new_location>`: Change the location of your existing account.
  - `!view_stats`: View your current stats.
  - Join game queues by clicking the buttons provided in the Discord channel.
 
## Demonstration

https://youtu.be/PT2EeLSU1jE

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
