# Setting Up Matlab-Style Command Completion in WSL

This guide will help you set up Matlab-style command completion in your Windows Subsystem for Linux (WSL) environment, which includes:
- Tab completion showing all possibilities on first press
- History search with arrow keys that filters based on what you've already typed
- Case-insensitive completion

## Step 1: Create the Completion Script

1. Open your WSL terminal
2. Create a new file called `.matlab-style-completion.sh` in your home directory:

```bash
nano ~/.matlab-style-completion.sh
```

3. Copy and paste the following content into the file:

```bash
#!/bin/bash

# Enable Matlab-style completion (case-insensitive, show all possibilities on first tab)
bind 'set show-all-if-ambiguous on'
bind 'set show-all-if-unmodified on'
bind 'set completion-ignore-case on'
bind 'set menu-complete-display-prefix on'
bind 'TAB:menu-complete'

# Set up history search with arrow keys
# This makes the up and down arrows search through history based on what you've typed
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'
```

4. Save the file by pressing `Ctrl+O`, then `Enter`, then exit nano with `Ctrl+X`

5. Make the script executable:

```bash
chmod +x ~/.matlab-style-completion.sh
```

## Step 2: Configure Your Bash Profile

1. Open your `.bashrc` file:

```bash
nano ~/.bashrc
```

2. Add the following lines at the end of the file:

```bash
# Load Matlab-style completion
if [ -f ~/.matlab-style-completion.sh ]; then
    source ~/.matlab-style-completion.sh
fi
```

3. Save and exit the file (`Ctrl+O`, `Enter`, `Ctrl+X`)

## Step 3: Apply the Changes

To apply the changes immediately without restarting your terminal:

```bash
source ~/.bashrc
```

## Testing the Setup

Now you can test the functionality:

1. **Tab completion**: Start typing a command and press `Tab` to see all possible completions
2. **History search**: Type the beginning of a command you've used before and press the `Up` arrow key to find matching commands from your history

## Troubleshooting

If the functionality doesn't work as expected:

1. Make sure your terminal is properly configured to send the correct escape sequences for arrow keys
2. Try restarting your WSL terminal
3. Check that the script was properly sourced by running: `echo $INPUTRC`

## Additional Customization

You can further customize the behavior by exploring additional readline options:

```bash
# To see all current bindings
bind -p

# To see all variables
bind -v
```