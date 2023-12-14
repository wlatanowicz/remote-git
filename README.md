Remote GIT wrapper
===

Motivation
---

Running git commands on network volume is extremely slow. This script allows you to cheat your git GUI and run git commands directly on the remote machine via ssh.


Installation and usage
---

To install the script make a symlink in your `$PATH`, ie.:

```bash
ln -s ./git.py ~/.local/bin/git
```

and adjust constants at the top of the file according to your setup.
