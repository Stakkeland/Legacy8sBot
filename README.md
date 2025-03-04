# Legacy8s Project

## Overview
Legacy8s is a Discord bot designed to manage game queues and facilitate 8s creations on legacy Call of Duty titles. 
It allows users to create accounts, join match queues, gain sr, and become a competitive Call of Duty grandmaster.

## Project Structure
```
Legacy8s
├── src
│   ├── bot.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── account.py
│   │   └── queue.py
│   ├── database
│   │   ├── __init__.py
│   │   └── db.py
│   ├── views
│   │   ├── __init__.py
│   │   └── queue_view.py
│   └── utils
│       ├── __init__.py
│       └── constants.py
├── users.db
├── requirements.txt
└── README.md
```

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using the following command:
   ```
   pip install -r requirements.txt
   ```
4. Ensure you have a valid Discord bot token and update it in the `bot.py` file.

## Usage
- Run the bot by executing the `bot.py` file:
  ```
  python src/bot.py
  ```
- Use the following commands in Discord:
  - `!create_account <location>`: Create a new user account with the specified location.
  - `!change_location <new_location>`: Change the location of your existing account.
  - Join game queues by clicking the buttons provided in the Discord channel.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.