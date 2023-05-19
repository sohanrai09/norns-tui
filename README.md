### Introduction

Goal of this little project was me to explore the amazing [Textual](https://textual.textualize.io/) library.
In this project, I'm building an `app` in the terminal using `Textual` to perform some basic networking related tasks. I've used [Nornir](https://nornir.readthedocs.io/en/latest/)
to do the underlying networking tasks.

As of now, `norns-tui` has three functions.
1. To look up a card in a list of devices.
2. To look up any pattern of configuration in a list of devices.
3. To fetch the output of any command across a list of devices.

For now, list of cards and commands used in function 1 and 3 respectively have been defined manually. May be in the future I can think of making this a
bit more dynamic.

Note: This only works on Juniper devices.

### `norns-tui` in action

https://github.com/sohanrai09/norns-tui/assets/89385413/6b807156-56f0-4935-818b-fbb41c17b7a2


### Reference

- [net-textorial](https://github.com/dannywade/net-textorial) by Danny Wade. Danny talks about his project on his [Youtube Channel](https://www.youtube.com/watch?v=H8uGOIK2ZqY), highly recommend following him.

- [Textual](https://textual.textualize.io/) has a very robust documentation, and they are always adding things to it to make it easier to explore.
