# Discord Bot

This project is a Discord bot built using Python. It utilizes the `discord.py` library to interact with the Discord API and includes a modular structure with cogs for extending functionality.

## Features

- Modular design using cogs for easy extension.
- Logging utilities to capture and send logs to a specified Discord channel.
- Environment variable management using a `.env` file.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd discord-bot
   ```

2. **Install dependencies:**
   Make sure you have Python 3.8 or higher installed. Then, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   In the root directory, create a `.env` file and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```

4. **Run the bot:**
   You can start the bot by running the following command:
   ```bash
   python -m src
   ```

## Usage

Once the bot is running, it will connect to your Discord server and start responding to commands defined in the cogs. You can customize the bot's behavior by modifying the cogs in the `src/cogs` directory.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the bot. 

## License

This project is licensed under the MIT License. See the LICENSE file for more details.