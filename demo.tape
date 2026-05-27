Output docs/demo.gif

Set Shell zsh
Env PATH "/Users/an/Development/aiq/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
Set FontSize 14
Set Width 900
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 16
Set Framerate 24
Set PlaybackSpeed 1

Require aiq

# Start
Type "aiq daemon start"
Enter
Sleep 1s

Type "aiq daemon status"
Enter
Sleep 500ms

# Configure
Sleep 300ms
Type `aiq model add nano --endpoint https://nano-gpt.com/api/subscription/v1 --api-key $NANO_API_KEY --model-id claw-medium -y`
Enter
Sleep 500ms

Type `aiq agent add writer --model nano --system-prompt "You are a concise technical writer." -y`
Enter
Sleep 500ms

Type "aiq group add drafts -y"
Enter
Sleep 500ms

# List everything
Type "aiq model"
Enter
Sleep 800ms

Type "aiq agent"
Enter
Sleep 800ms

Type "aiq group"
Enter
Sleep 800ms

# Queue tasks
Sleep 300ms
Type `aiq add "Explain what a Merkle tree is in two sentences." -g drafts -a writer -y`
Enter
Sleep 500ms

Type `aiq add "Now give a one-line analogy for the above." -g drafts -a writer --after 0 -y`
Enter
Sleep 500ms

# Watch status — task 0 running
Type "aiq status"
Enter
Sleep 2s

# Wait for task 0 to finish, then show status again
Sleep 8s
Type "aiq status"
Enter
Sleep 2s

# Read outputs
Type "aiq log 0"
Enter
Sleep 1s

Type "aiq log 1"
Enter
Sleep 1s

# Inspect the generated script
Type "aiq script 0"
Enter
Sleep 2s

# Stop
Type "aiq daemon stop"
Enter
Sleep 1s
