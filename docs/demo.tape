Output docs/demo.gif

Set Shell zsh
Set FontSize 14
Set Width 900
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 16
Set Framerate 24
Set PlaybackSpeed 1
Env PATH "/Users/an/Development/aiq/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

Require aiq

# Silent setup
Hide
Type `export PS1="% "`
Enter
Sleep 200ms
Type "aiq start"
Enter
Sleep 2s
Type `aiq model add nano --endpoint https://nano-gpt.com/api/subscription/v1 --api-key $NANO_API_KEY --model-id claw-medium -y`
Enter
Sleep 500ms
Type `aiq agent add coder --model nano --system-prompt "You are an expert Python developer. Reply with code only, no explanation." -y`
Enter
Sleep 500ms
Type `aiq agent add reviewer --model nano --system-prompt "You are a senior code reviewer. Be concise and specific." -y`
Enter
Sleep 500ms
Type "clear"
Enter
Sleep 300ms
Show

# Task 0
Type `aiq add "Write a Python function for Fibonacci." -a coder`
Enter
Sleep 500ms
Type "y"
Enter
Sleep 500ms

# Task 1
Type `aiq add "Write pytest unit tests for the above function." -a coder --after 0`
Enter
Sleep 500ms
Type "y"
Enter
Sleep 500ms

# Task 2
Type `aiq add "Review the code above for correctness and style." -a reviewer --after 0`
Enter
Sleep 500ms
Type "y"
Enter
Sleep 500ms

# Status — all queued
Type "aiq status"
Enter
Sleep 5s

# Wait for all three to complete
Hide
Sleep 60s
Show

# Status — all done
Type "aiq status"
Enter
Sleep 5s

# Read results
Type "aiq log 0"
Enter
Sleep 5s

Type "aiq log 1"
Enter
Sleep 5s

Type "aiq log 2"
Enter
Sleep 5s
