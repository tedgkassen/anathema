""""
Provides utilities for processing custom user commands
"""

import re
from handler import Handler


class CommandHandler(Handler):
    """Handles user custom cammands."""
    def __init__(self, storage, handlers):
        self.storage = storage
        self.handlers = handlers

        commands = storage.get('commands') or {}
        self.commands = commands

    def accepts(self, message):
        if message.content.startswith('!set-command') or message.content.strip(
        ) == '!clear-commands':
            return True
        command = self._extract_command(message)
        author_commands = self.commands.get(str(message.author.id), {})
        return bool(author_commands.get(command, False))

    def _extract_command(self, message):
        """Finds user command token from input"""
        first_space_idx = message.content.find(' ')
        command_end = first_space_idx if first_space_idx > 0 else len(
            message.content)
        return message.content[1:command_end]

    def _get_author_commands(self, author_id):
        return self.commands.get(str(author_id), {})

    def _set_author_command(self, author_id, hot_word, command):
        author_commands = self._get_author_commands(author_id)
        author_commands[hot_word] = command
        self._set_author_commands(author_id, author_commands)

    def _set_author_commands(self, author_id, commands):
        self.commands[str(author_id)] = commands

    def _flush_commands(self):
        self.storage.put('commands', self.commands)

    # Response Handlers

    async def process(self, message):
        if not self.accepts(message):
            return

        if message.content.startswith('!set-command'):
            await message.channel.send(self.get_set_command_response(message))
        elif message.content.strip() == '!clear-commands':
            await message.channel.send(self.get_clear_command_response(message)
                                       )
        else:
            await self.process_user_command(message)

    def get_set_command_response(self, message):
        """Responds to command to set user command"""
        command_clause_end = message.content.find('::')
        command_clause = message.content[12:command_clause_end].strip()
        if not re.match(r'[a-zA-Z0-9\-_]+', command_clause):
            return "Command can only be alphanumber characters, -, and _"

        command = message.content[command_clause_end + 2:].strip()

        self._set_author_command(message.author.id, command_clause, command)
        self._flush_commands()

        return '{} registered command: `!{}` -> `{}`'.format(
            message.author.nick, command_clause, command)

    def get_clear_command_response(self, message):
        """Responds to command to clear user command"""
        self.commands[str(message.author.id)] = {}
        self._flush_commands()

        return '{} has cleard all commands.'.format(message.author.nick)

    async def process_user_command(self, message):
        """Expands command and runs"""
        command = self._extract_command(message)
        mapping = self.commands[str(message.author.id)][command]

        command_input = message.content.strip()

        seperator_idx = command_input.find(' ')

        args = ''
        if seperator_idx > 0:
            args = command_input[seperator_idx:].strip()

        new_message_content = mapping.replace('{}', args, 1)
        message.content = new_message_content

        for handler in self.handlers:
            await handler.process(message)
