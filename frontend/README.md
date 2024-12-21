# Congress.Dev Frontend

This is a standard react app. It is intended to be served via docker, so you should follow the instructions to run the entire app from the top level readme.

## Running

```bash
yarn start
```

## Windows Development w/ VSCode

- Install Prettier extension for VSCode
- Install Node.js for Windows (reboot after installing)
- Run Powershell as Administrator
    - Execute `Set-ExecutionPolicy Unrestricted`
- Run `yarn install`
- To format code:
    - Open command pallete in VSCode with `Ctrl+Shift+P` and run `Format Document`
    - OR: Run `yarn format` to format code for all files before creating pull request
