from nornir import InitNornir
from nornir_pyez.plugins.tasks import pyez_rpc
from textual.app import App, ComposeResult
from textual.containers import Container, Content, Grid
from textual.widgets import Header, Footer, Input, Static, Button, Label
from rich.syntax import Syntax
from rich.text import Text
from rich.console import Console
from nornir_napalm.plugins.tasks import napalm_cli
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem
from textual.screen import ModalScreen
import re
import datetime

today = datetime.date.today()
console = Console()

nr = InitNornir(config_file='norn_inv/config.yaml')

with open('card_inventory.txt', 'r') as f:
    card_inv = f.readlines()

with open('cli_commands.txt', 'r') as f:
    cli_inv = f.readlines()

cards = []
cli_cmds = []

for card in card_inv:
    cards.append(DropdownItem(card.strip()))

for cli in cli_inv:
    cli_cmds.append(DropdownItem(cli.strip()))


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


class Devicelogin(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "my_app.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("q", "request_quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Container(
            AutoComplete(Input(
                placeholder="Enter the card name to lookup",
                id="card_name"),
                Dropdown(items=cards, id='card_dropdown')),

            Button(label="Clear!", variant="primary", id="clear_button"),
            id="card_container",
        )

        yield Container(Input(
            placeholder="Search the configs for :",
            id="cfg"),

            Button(label="Search!", variant="primary", id="search_button"),
            id="cfg_container",
        )

        yield Container(AutoComplete(Input(
            placeholder="Fetch output of commands from all devices :",
            id="cmds"),
            Dropdown(items=cli_cmds, id='cli_dropdown')),

            Button(label="Fetch!", variant="primary", id="fetch_button"),
            id="cmd_container",
        )

        yield Label(id='searching')

        yield Content(
            Static(Text("~~~ Results ~~~", justify="center"), classes="result-header"),
            Static(id="raw-results", classes="result"),
            classes="results-container",
        )

        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        # Give the input focus, so we can start typing straight away
        self.query_one("#card_name").focus()

    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Run when user clicks a button"""
        if event.button.id == 'clear_button':
            self.query_one("#card_name").action_delete_left_all()
            self.query_one("#cfg").action_delete_left_all()
            self.query_one("#cmds").action_delete_left_all()
            self.query_one("#raw-results", Static).update('')
        elif event.button.id == 'search_button':
            cfg_src = self.query_one("#cfg")
            if cfg_src.value:
                self.cfg_fetch(cfg_src.value)
        elif event.button.id == 'fetch_button':
            cmds = self.query_one("#cmds")
            if cmds.value:
                self.cmd_fetch(cmds.value)

    def on_auto_complete_selected(self, event) -> None:
        """Run when user hits tab or enter after selecting the input from the dropdown"""
        user_input = self.query_one("#card_name")
        if user_input.value:
            # Get user input when user hits tab
            self.card_fetch(user_input.value)

    def card_fetch(self, card_name):
        card_search_output = nr.run(task=pyez_rpc, func='get-chassis-inventory')
        router_list = list(dict.keys(card_search_output))

        final_card_result = ''
        for router in router_list:
            card_result = card_search_output[router][0].result
            module_list = card_result['chassis-inventory']['chassis']['chassis-module']
            for module in module_list:
                if 'FPC' in module['name'] and card_name == module['model-number']:
                    final_card_result = f": {router} : {module['name']} > {module['model-number']}" + \
                                        '\n' + final_card_result

        if final_card_result != '':
            self.query_one("#raw-results", Static).update(Syntax(final_card_result, "teratermmacro",
                                                                 theme="vs", line_numbers=True))
        else:
            self.query_one("#raw-results", Static).update(Syntax('Card Not Found!', "teratermmacro",
                                                                 theme="dracula", line_numbers=True))

    def cfg_fetch(self, cfg_search):
        cfg_search_output = nr.run(task=napalm_cli, commands=[f'show configuration | display set | match {cfg_search}'])
        router_list = list(dict.keys(cfg_search_output))

        cfg_search_result = ''
        for router in router_list:
            cfg_result = cfg_search_output[router][0].result
            for key, value in cfg_result.items():
                if value != "":
                    cfg_search_result = cfg_search_result + f'~~ Config found in {router} ~~\n{value}\n\n'

        if cfg_search_result != '':
            self.query_one("#raw-results", Static).update(Syntax(cfg_search_result, "teratermmacro",
                                                                 theme="dracula", line_numbers=True))
        else:
            self.query_one("#raw-results", Static).update(Syntax('~~ Config not found anywhere! ~~', "teratermmacro",
                                                                 theme="dracula", line_numbers=True))

    def cmd_fetch(self, cmds):
        cmds_list = cmds.split(',')
        cmd_fetch_output = nr.run(task=napalm_cli, commands=cmds_list)
        router_list = list(dict.keys(cmd_fetch_output))

        cmd_fetch_result = ''
        for router in router_list:
            cmd_result = cmd_fetch_output[router][0].result
            cmd_str = re.sub(" ", "_", cmds)
            final_out = cmd_result[cmds]
            cmd_fetch_result = cmd_fetch_result + f"^^^ {today}/{cmd_str}/{router} ^^^^\n\n{final_out.strip()}\n\n\n"
        self.query_one("#raw-results", Static).update(Syntax(cmd_fetch_result, "teratermmacro",
                                                             theme="dracula", line_numbers=True))


if __name__ == "__main__":
    app = Devicelogin()
    app.run()
